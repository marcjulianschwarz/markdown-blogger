from datetime import datetime as dt
from pathlib import Path
from typing import List

from frontmatter import Post

from blogger.constants import (
    BLOG_AUTHOR_KEY,
    BLOG_SUBTITLE_KEY,
    BLOG_TAGS_KEY,
    BLOG_TITLE_KEY,
)
from blogger.tag import Tag
from blogger.utils import get_date, is_archived


class BlogPost:
    def __init__(self, post_meta: Post, markdown_file: Path):
        self.title = post_meta.get(BLOG_TITLE_KEY) or markdown_file.stem
        self.subtitle = post_meta.get(BLOG_SUBTITLE_KEY) or ""
        self.author = post_meta.get(BLOG_AUTHOR_KEY) or "Marc Julian Schwarz"
        self.desc = f"{self.title} - {self.subtitle} - {self.author}"
        self.content = post_meta.content
        self.markdown_file = markdown_file
        self.id = markdown_file.stem
        self.last_modified = dt.fromtimestamp(markdown_file.stat().st_mtime)

        self.date = get_date(post_meta)
        self.display_year = str(self.date.year)
        self.display_month = str(self.date.month).zfill(2)

        self.tags = self.get_tags(post_meta)

        self.archived = is_archived(post_meta)
        self.html_path = Path(self.markdown_file.stem)

    def get_tags(self, post_meta: Post) -> List[Tag]:
        found_tags = []
        keys = ["tag", BLOG_TAGS_KEY]
        for key in keys:
            found_tags.extend(post_meta.get(key, []))

        tags = [
            Tag(
                name=tag.strip(),
                color="tag-post",
            )
            for tag in found_tags
        ]
        tags.append(
            Tag(
                name=self.date.year,
                color="tag-year",
            ),
        )
        return tags

    def to_json(self):
        return {
            "title": self.title,
            "subtitle": self.subtitle,
            "author": self.author,
            "desc": self.desc,
            "content": self.content,
            "markdown_file": str(self.markdown_file),
            "date": self.date.strftime("%Y-%m-%d"),
            "display_year": self.display_year,
            "display_month": self.display_month,
            "tags": [tag.to_json() for tag in self.tags],
            "archived": self.archived,
            "html_path": str(self.html_path),
            "last_modified": self.last_modified.strftime("%Y-%m-%d"),
            "id": self.id,
        }

    def to_json_sparse(self):
        return {
            "markdown_file": str(self.markdown_file),
            "date": self.date.strftime("%Y-%m-%d"),
            "tags": [tag.id for tag in self.tags],
            "last_modified": self.last_modified.strftime("%Y-%m-%d"),
            "id": self.id,
        }

    @classmethod
    def from_json(cls, data: dict):
        post = cls.__new__(cls)
        post.title = data["title"]
        post.subtitle = data["subtitle"]
        post.author = data["author"]
        post.desc = data["desc"]
        post.content = data["content"]
        post.markdown_file = Path(data["markdown_file"])
        post.date = dt.strptime(data["date"], "%Y-%m-%d").date()
        post.display_year = data["display_year"]
        post.display_month = data["display_month"]
        post.tags = [Tag.from_json(tag) for tag in data["tags"]]
        post.archived = data["archived"]
        post.html_path = Path(data["html_path"])
        post.last_modified = dt.strptime(data["last_modified"], "%Y-%m-%d")
        post.id = data["id"]
        return post

    @classmethod
    def from_json_sparse(cls, data: dict):
        post = cls.__new__(cls)
        post.markdown_file = Path(data["markdown_file"])
        post.date = dt.strptime(data["date"], "%Y-%m-%d").date()
        post.tags = [Tag(id=tag) for tag in data["tags"]]
        post.last_modified = dt.strptime(data["last_modified"], "%Y-%m-%d")
        post.id = data["id"]
        return post
