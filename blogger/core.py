import os
from datetime import datetime as dt
from pathlib import Path
from typing import List

import markdown2
from frontmatter import Post
from blogger.constants import (
    BLOG_ARCHIVED_KEY,
    BLOG_AUTHOR_KEY,
    BLOG_DATE_KEY,
    BLOG_PUBLISHED_KEY,
    BLOG_SKIP_KEY,
    BLOG_SUBTITLE_KEY,
    BLOG_TAGS_KEY,
    BLOG_TITLE_KEY,
)

from blogger.templates import Header, Templates
from blogger.utils import *


class Tag:
    def __init__(self, name: str | int, link: str, color: str) -> None:
        self.name = str(name)
        self.link = link
        self.color = color

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, o: object) -> bool:
        return self.name == o.name and self.link == o.link and self.color == o.color

    def lower(self):
        return self.name.lower()

    def __repr__(self) -> str:
        return f"Tag(name={self.name}, link={self.link}, color={self.color})"

    def __lt__(self, other):
        return self.name < other.name

    def __gt__(self, other):
        return self.name > other.name

    def __le__(self, other):
        return self.name <= other.name

    def __ge__(self, other):
        return self.name >= other.name


def get_no_none(objects):
    return [x for x in objects if x is not None]


def get_date(post: Post):
    date = get_no_none(
        [
            post.get(BLOG_DATE_KEY),
            post.get("Date"),
            post.get("DATE"),
            post.get(BLOG_PUBLISHED_KEY),
        ]
    )
    if len(date) == 0:
        return dt(1970, 1, 1)
    # elif type(date[0]) == str:
    #     try:
    #         return dt.strptime(date[0], "%Y-%m-%d")
    #     except:
    #         return dt(1970, 1, 1)
    else:
        return date[0]


def get_tags(post: Post) -> List[Tag]:
    tags = post.get(BLOG_TAGS_KEY, [])
    tags2 = post.get("tag", [])
    tags.extend(tags2)

    return [
        Tag(name=tag.strip(), link=f"tags/{tag.strip()}.html", color="tag-post")
        for tag in tags
    ]


class TagList:
    def __init__(self, tags: List[Tag]) -> None:
        self.tags = tags

    def valid_tag_name(self, tag_name: str) -> bool:
        return tag_name != "" and tag_name != "blog"

    def render(self, output_path: Path, blog_mode: BlogMode) -> str:
        tags_html = ""
        for tag in self.tags:
            if tag and self.valid_tag_name(tag.name):
                tags_html += Templates.tag().render(
                    name=str(tag.name),
                    link="/" + tag.link
                    if blog_mode == BlogMode.WEB
                    else output_path / tag.link,
                    color_class=tag.color,
                )
        return tags_html


class BlogPost:
    def __init__(self, post_meta: Post, file: Path):
        self.title = post_meta.get(BLOG_TITLE_KEY) or file.stem
        self.subtitle = post_meta.get(BLOG_SUBTITLE_KEY) or ""
        self.author = post_meta.get(BLOG_AUTHOR_KEY) or "Marc Julian Schwarz"
        self.desc = f"{self.title} - {self.subtitle} - {self.author}"
        self.content = post_meta.content
        self.path = file

        self.date = (
            get_date(post_meta) if not self._is_demo(post_meta) else dt.now().date()
        )
        self.tags = get_tags(post_meta)

        self.archived = self.date.year < 2021 or self._is_archived(post_meta)

    def _render(self, output_path: Path, blog_mode: BlogMode) -> str:
        html = markdown2.markdown(
            self.content,
            extras=MARKDOWN_EXTRAS,
        )

        tags = [
            *self.tags,
            Tag(
                name=self.date.year,
                link=f"year/{self.date.year}.html",
                color="tag-year",
            ),
        ]

        tag_list = TagList(tags).render(output_path, blog_mode)

        meta = Templates.meta().render(
            meta_desc=self.desc,
            meta_author=self.author,
            meta_keywords=",".join([tag.name for tag in tags]),
        )

        post_html = Templates.post().render(
            content=html,
            title=self.title,
            subtitle=self.subtitle,
            author=self.author,
            date=self.date.strftime("%d.%m.%Y") or "",
            tags=tag_list,
            meta=meta,
            header=Header.render(blog_mode, output_path),
        )

        if blog_mode == BlogMode.LOCAL:
            post_html = post_html.replace("/images/", str(output_path) + "/images/")

        return post_html

    def _create_dir(self, dir: str):
        if not os.path.exists(dir):
            os.makedirs(dir)

    def save(self, output_path: Path, blog_mode: BlogMode):
        post_html = self._render(output_path, blog_mode)

        path = output_path / "posts" / str(self.date.year) / str(self.date.month)
        self._create_dir(path)

        with open(path / f"{self.path.stem}.html", "w") as f:
            f.write(post_html)

    def _is_property(self, key: str, post: Post) -> bool:
        return key in post.keys() and post[key] is not None and post[key] != ""

    def _is_demo(self, post: Post) -> bool:
        if self._is_property(BLOG_SKIP_KEY, post):
            return post[BLOG_SKIP_KEY]
        else:
            return False

    def _is_archived(self, post_meta: Post) -> bool:
        if self._is_property(BLOG_ARCHIVED_KEY, post_meta):
            return post_meta[BLOG_ARCHIVED_KEY]
        else:
            return False


class BlogPostList:
    def __init__(self, post: List[BlogPost]) -> None:
        self.posts = post

    def _render_blog_post(
        self, post: BlogPost, output_path: Path, blog_mode: BlogMode
    ) -> str:
        subtitle = " - " + post.subtitle if post.subtitle != "" else ""

        post_url = (
            str(
                output_path
                / "posts"
                / str(post.date.year)
                / str(post.date.month)
                / f"{post.path.stem}.html"
            )
            if blog_mode == BlogMode.LOCAL
            else f"/posts/{post.date.year}/{post.date.month}/{post.path.stem}.html"
        )

        return Templates.post_list_entry().render(
            title=post.title,
            subtitle=subtitle,
            author=post.author,
            date=post.date.strftime("%d.%m.%Y"),
            tags_list=TagList(post.tags).render(output_path, blog_mode),
            link=post_url,
        )

    def render(self, output_path: Path, blog_mode: BlogMode) -> str:
        post_list = ""
        for post in sorted(self.posts, key=lambda x: x.date, reverse=True):
            post_entry = self._render_blog_post(post, output_path, blog_mode)
            post_list += post_entry
        return post_list


class TagPage:
    def __init__(self, tag: Tag, posts: List[BlogPost]) -> None:
        self.tag = tag
        self.posts = posts

    def _create_dir(self, dir: str):
        if not os.path.exists(dir):
            os.makedirs(dir)

    def _render(self, output_path: Path, blog_mode: BlogMode) -> str:
        post_list = BlogPostList(self.posts).render(output_path, blog_mode)

        return Templates.tag_page().render(
            name=self.tag.name,
            count=len(self.posts),
            post_list=post_list,
            header=Header().render(blog_mode, output_path),
        )

    def save(self, blog_mode: BlogMode, output_path: Path):
        tag_output_path = output_path / self.tag.link
        self._create_dir(tag_output_path.parent)
        html = self._render(output_path, blog_mode)
        with open(tag_output_path, "w") as f:
            f.write(html)
