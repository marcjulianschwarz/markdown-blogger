import os
import urllib.parse
import webbrowser
from datetime import datetime as dt
from pathlib import Path

import frontmatter
from frontmatter import Post
from tqdm import tqdm

from blogger.blog_index import BlogIndex
from blogger.constants import (
    BLOG_ARCHIVED_KEY,
    BLOG_DATE_KEY,
    BLOG_DEMO_VALUE,
    BLOG_PUBLISHED_KEY,
    BLOG_SKIP_KEY,
)
from blogger.core import BlogPost, TagPage
from blogger.sitemap import Sitemap
from blogger.utils import *


class Blog:
    def __init__(
        self,
        markdown_path: str,
        output_path: str,
        mode: BlogMode = BlogMode.LOCAL,
        show_demo: bool = False,
    ):
        self.input = Path(markdown_path)
        self.output = Path(output_path)
        self.mode = mode

        if self.mode == BlogMode.WEB:
            self.show_demo = False
        else:
            self.show_demo = show_demo

        self.blog_index = BlogIndex()
        self.sitemap = Sitemap()

    def _is_skip(self, post: Post) -> bool:
        if self._is_property(BLOG_SKIP_KEY, post):
            return post[BLOG_SKIP_KEY] == 1

        if self.show_demo:
            return False
        else:
            return self._is_demo(post)

    def _is_property(self, key: str, post: Post) -> bool:
        return key in post.keys() and post[key] is not None and post[key] != ""

    def _is_demo(self, post: Post) -> bool:
        if self._is_property(BLOG_PUBLISHED_KEY, post):
            return post[BLOG_PUBLISHED_KEY] == "demo"
        elif self._is_property(BLOG_DATE_KEY, post):
            return post[BLOG_DATE_KEY] == BLOG_DEMO_VALUE
        else:
            return True

    def _is_archived(self, post_meta: Post) -> bool:
        if self._is_property(BLOG_ARCHIVED_KEY, post_meta):
            return post_meta[BLOG_ARCHIVED_KEY] == 1

    def build_index_and_create_posts(self):
        markdown_files = list(self.input.glob("*.md"))
        for file in (pbar := tqdm(markdown_files)):
            pbar.set_description(f"Creating {file.name}")
            with open(file, "r") as f:
                file_content = f.read()

                post_meta = frontmatter.loads(file_content)
                last_modified = dt.fromtimestamp(os.path.getmtime(file))

                if self._is_skip(post_meta):
                    continue

                post = BlogPost(post_meta, file)
                self.blog_index.add_post(post)
                self.sitemap.update_sitemap(
                    url=f"https://www.marc-julian.de/posts/{str(post.date.year)}/{str(post.date.month)}/{urllib.parse.quote(file.stem)}.html",
                    lastmod=last_modified.strftime("%Y-%m-%d"),
                )
                post.save(self.output, self.mode)

    def create_tag_pages(self):
        for tag in (pbar := tqdm(self.blog_index.tags)):
            pbar.set_description(f"{tag.name}")
            posts = [
                post
                for post in self.blog_index.posts
                if tag in post.tags
                or post.date.year == (tag.name.isnumeric() and int(tag.name))
            ]
            # print("Found", len(posts), "posts for tag", tag.name)
            tag_page = TagPage(tag, posts)
            tag_page.save(self.mode, self.output)

    def delete_posts(self):
        post_files = list(self.output.glob("posts/**/*.html"))
        for file in (pbar := tqdm(post_files)):
            pbar.set_description(f"Deleting {file.name}")
            file.unlink()

    def delete_tags(self):
        tag_files = list(self.output.glob("tags/**/*.html"))
        for file in (pbar := tqdm(tag_files)):
            pbar.set_description(f"Deleting {file.name}")
            file.unlink()

    def delete_years(self):
        year_files = list(self.output.glob("year/**/*.html"))
        for file in (pbar := tqdm(year_files)):
            pbar.set_description(f"Deleting {file.name}")
            file.unlink()

    def delete_output(self):
        self.delete_posts()
        self.delete_tags()
        self.delete_years()

    def open_index(self):
        webbrowser.open("file://" + os.path.realpath(self.output / "index.html"), new=0)

    def create_index(self):
        self.blog_index.save_index(self.mode, self.output)

    def create_sitemap(self):
        self.sitemap.save_sitemap(self.output)
