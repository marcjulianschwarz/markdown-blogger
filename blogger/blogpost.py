from datetime import datetime as dt
from pathlib import Path
from typing import List

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
from blogger.tag import Tag
from blogger.utils import get_date, has_property, is_archived


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
        self.display_year = str(self.date.year)
        self.display_month = str(self.date.month).zfill(2)

        self.tags = self.get_tags(post_meta)

        self.archived = self.date.year < 2021 or is_archived(post_meta)
        self.post_url = (
            f"/{self.display_year}/{self.display_month}/{self.path.stem}.html"
        )

    def get_tags(self, post_meta: Post) -> List[Tag]:
        found_tags = post_meta.get(BLOG_TAGS_KEY, [])
        tags2 = post_meta.get("tag", [])
        found_tags.extend(tags2)

        tags = [
            Tag(
                name=tag.strip(),
                color="tag-post",
                path=TAGS_PATH,
            )
            for tag in found_tags
        ]
        tags.append(
            Tag(
                name=self.date.year,
                color="tag-year",
                path=YEARS_PATH,
            ),
        )
        return tags

    def save(self, output_path: Path, post_html: str):
        path = output_path / self.display_year / self.display_month
        path.mkdir(parents=True, exist_ok=True)
        (path / f"{self.path.stem}.html").write_text(post_html)

    def _is_demo(self, post: Post) -> bool:
        if has_property(BLOG_SKIP_KEY, post):
            return post[BLOG_SKIP_KEY]
        else:
            return False
