import urllib.parse
from datetime import datetime as dt
from pathlib import Path

import frontmatter
from tqdm import tqdm

from blogger.blog_index import BlogIndex
from blogger.blogpost import BlogPost
from blogger.constants import TAGS_PATH
from blogger.render import render_blog_post, render_tag_page
from blogger.sitemap import Sitemap
from blogger.utils import is_demo, is_skip


class Blog:
    def __init__(
        self,
        markdown_path: str,
        output_path: str,
        show_demo: bool = False,
    ):
        self.input = Path(markdown_path)
        self.output = Path(output_path)
        self.show_demo = show_demo

        # Initialize blog index and sitemap file
        self.blog_index = BlogIndex()
        self.sitemap = Sitemap()

    def build_index_and_create_posts(self):
        """
        Builds the blog index and updates the sitemap file.
        1. Read markdown file from markdown path
        2. Load metadata from frontmatter and file object
        3. Check if post should be skipped
        4. Create BlogPost object
        5. Add post to blog index
        6. Update sitemap
        7. Save post
        """
        markdown_files = list(self.input.glob("*.md"))
        for file in (pbar := tqdm(markdown_files)):
            pbar.set_description(f"Creating {file.name}")

            file_content = file.read_text()
            post_meta = frontmatter.loads(file_content)
            last_modified = dt.fromtimestamp(file.stat().st_mtime)
            post = BlogPost(post_meta, file)
            post_html = render_blog_post(post)
            post.save(self.output, post_html)

            self.blog_index.add_post(post)

            self.sitemap.update_sitemap(
                url=f"https://www.marc-julian.de/posts/{str(post.date.year)}/{str(post.date.month)}/{urllib.parse.quote(file.stem)}.html",
                lastmod=last_modified.strftime("%Y-%m-%d"),
            )

    def create_tag_pages(self):
        for tag in (pbar := tqdm(self.blog_index.tags)):
            pbar.set_description(f"{tag.name}")
            posts = [
                post
                for post in self.blog_index.posts
                if tag in post.tags
                or post.date.year == (tag.name.isnumeric() and int(tag.name))
            ]

            tag_page = render_tag_page(tag, posts)
            (self.output / TAGS_PATH / f"{tag.name}.html").write_text(tag_page)

    def create_index(self):
        self.blog_index.save_index(self.output)

    def create_sitemap(self):
        self.sitemap.save_sitemap(self.output)
