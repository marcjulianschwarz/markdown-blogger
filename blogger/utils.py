from datetime import datetime as dt
from enum import Enum

from frontmatter import Post

from blogger.constants import (
    BLOG_ARCHIVED_KEY,
    BLOG_DATE_KEY,
    BLOG_DEMO_VALUE,
    BLOG_PUBLISHED_KEY,
    BLOG_SKIP_KEY,
)

# these are extensions for the markdown2 package
# see https://github.com/trentm/python-markdown2/wiki/Extras for more
MARKDOWN_EXTRAS = [
    "code-friendly",
    "fenced-code-blocks",
    "cuddled-lists",
    # "metadata", # -> bug where first line will not be parsed
    "tables",
    "spoiler",
    "task-lists",
    "wiki-tables",
    "mermaid",
    "tag-friendly",
    # "target-blank-links",
    "strike",
]


class BlogMode(Enum):
    """Depending on the blog mode the output will either be made with local absolute paths or web relative paths."""

    LOCAL = "local"
    WEB = "web"


def is_skip(post: Post) -> bool:
    if has_property(BLOG_SKIP_KEY, post):
        return post[BLOG_SKIP_KEY] == 1


def has_property(key: str, post: Post) -> bool:
    return key in post.keys() and post[key] is not None and post[key] != ""


def is_demo(post: Post) -> bool:
    if has_property(BLOG_PUBLISHED_KEY, post):
        return post[BLOG_PUBLISHED_KEY] == "demo"
    elif has_property(BLOG_DATE_KEY, post):
        return post[BLOG_DATE_KEY] == BLOG_DEMO_VALUE
    else:
        return True


def is_archived(post_meta: Post) -> bool:
    if has_property(BLOG_ARCHIVED_KEY, post_meta):
        return post_meta[BLOG_ARCHIVED_KEY] == 1


def get_date(post: Post):
    date = filter(
        lambda x: x is not None,
        [
            post.get(BLOG_DATE_KEY),
            post.get("Date"),
            post.get("DATE"),
            post.get(BLOG_PUBLISHED_KEY),
        ],
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
