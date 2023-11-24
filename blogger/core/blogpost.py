from datetime import datetime as dt
from pathlib import Path
from typing import List

import markdown2
from frontmatter import Post

from blogger.constants import (
    BLOG_AUTHOR_KEY,
    BLOG_SKIP_KEY,
    BLOG_SUBTITLE_KEY,
    BLOG_TAGS_KEY,
    BLOG_TITLE_KEY,
    TAGS_PATH,
    YEARS_PATH,
)
from blogger.core import Tag, render_tag_list
from blogger.templates import Header, Templates
from blogger.utils import MARKDOWN_EXTRAS, get_date, has_property, is_archived


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
        year = str(self.date.year)
        month = str(self.date.month).zfill(2)

        self.tags = self.get_tags(post_meta)

        self.archived = self.date.year < 2021 or is_archived(post_meta)
        self.post_url = f"/posts/{year}/{month}/{self.path.stem}.html"

    def get_tags(self, post_meta: Post) -> List[Tag]:
        found_tags = post_meta.get(BLOG_TAGS_KEY, [])
        tags2 = post_meta.get("tag", [])
        found_tags.extend(tags2)

        tags = [
            Tag(
                name=tag.strip(),
                path=f"{TAGS_PATH}/{tag.strip()}.html",
                color="tag-post",
            )
            for tag in found_tags
        ]
        tags.append(
            Tag(
                name=self.date.year,
                path=f"/{YEARS_PATH}/{self.date.year}.html",
                color="tag-year",
            ),
        )
        return tags

    def render(self) -> str:
        html = markdown2.markdown(
            self.content,
            extras=MARKDOWN_EXTRAS,
        )

        tag_list = render_tag_list(self.tags)

        meta = Templates.meta().render(
            meta_desc=self.desc,
            meta_author=self.author,
            meta_keywords=",".join([tag.name for tag in self.tags]),
        )

        post_html = Templates.post().render(
            content=html,
            title=self.title,
            subtitle=self.subtitle,
            author=self.author,
            date=self.date.strftime("%d.%m.%Y") or "",
            tags=tag_list,
            meta=meta,
            header=Header.render(),
        )

        # TODO: fix images / media
        # if blog_mode == BlogMode.LOCAL:
        #     post_html = post_html.replace("/images/", str(output_path) + "/images/")

        return post_html

    def save(self, output_path: Path, post_html: str):
        path = output_path / str(self.date.year) / str(self.date.month)
        path.mkdir(parents=True, exist_ok=True)
        (path / f"{self.path.stem}.html").write_text(post_html)

    def _is_demo(self, post: Post) -> bool:
        if has_property(BLOG_SKIP_KEY, post):
            return post[BLOG_SKIP_KEY]
        else:
            return False
