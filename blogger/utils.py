import http.server
import os
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
    "fenced-code-blocks",
    "code-friendly",
    "latex",
    "strike",
    "cuddled-lists",
    "tables",
    "wiki-tables",
    "mermaid",
    "tag-friendly",
]


def is_skip(post: Post) -> bool:
    if has_property(BLOG_SKIP_KEY, post):
        return post[BLOG_SKIP_KEY]


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
        return post_meta[BLOG_ARCHIVED_KEY]


def get_date(post: Post):
    date = list(
        filter(
            lambda x: x is not None,
            [
                post.get(BLOG_DATE_KEY),
                post.get("Date"),
                post.get("DATE"),
                post.get(BLOG_PUBLISHED_KEY),
            ],
        )
    )
    if len(date) == 0:
        return dt(1970, 1, 1).date()
    elif type(date[0]) == str:
        try:
            return dt.strptime(date[0], "%Y-%m-%d")
        except:
            return dt(1970, 1, 1).date()

    else:
        return date[0]


def create_http_handler(directory):
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            self.directory = directory
            super().__init__(*args, directory=directory, **kwargs)

        def translate_path(self, path):
            path = os.path.normpath(path)
            return os.path.join(self.directory, path.lstrip("/"))

    return Handler
