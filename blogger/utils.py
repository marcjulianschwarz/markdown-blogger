from enum import Enum

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
    LOCAL = "local"
    WEB = "web"
