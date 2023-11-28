from typing import List

import markdown2

from blogger.blogpost import BlogPost
from blogger.tag import Tag
from blogger.templates import Header, Templates
from blogger.utils import MARKDOWN_EXTRAS


def _valid_tag_name(tag_name: str) -> bool:
    return tag_name != "" and tag_name != "blog"


def render_tag_list(tags: List[Tag]) -> str:
    tags_html = ""
    for tag in tags:
        if tag and _valid_tag_name(tag.name):
            tags_html += Templates.tag().render(
                name=str(tag.name), link=f"/tags/{tag.id}.html", color_class=tag.color
            )
    return tags_html


def render_blog_list(posts: BlogPost) -> str:
    post_list = ""
    for post in sorted(posts, key=lambda x: x.date, reverse=True):
        post_entry = Templates.post_list_entry().render(
            title=post.title,
            subtitle=post.subtitle,
            author=post.author,
            date=post.date.strftime("%d.%m.%Y"),
            link=post.post_url,
        )
        post_list += post_entry
    return post_list


def render_tag_page(tag: Tag, posts: List[BlogPost]) -> str:
    post_list = render_blog_list(posts)
    return Templates.tag_page().render(
        name=tag.name,
        count=len(posts),
        post_list=post_list,
        header=Header().render(),
    )


def render_blog_post(post: BlogPost) -> str:
    html = markdown2.markdown(
        post.content,
        extras=MARKDOWN_EXTRAS,
    )

    tag_list = render_tag_list(post.tags)

    meta = Templates.meta().render(
        meta_desc=post.desc,
        meta_author=post.author,
        meta_keywords=",".join([tag.name for tag in post.tags]),
    )

    post_html = Templates.post().render(
        content=html,
        title=post.title,
        subtitle=post.subtitle,
        author=post.author,
        date=post.date.strftime("%d.%m.%Y") or "",
        tags=tag_list,
        meta=meta,
        header=Header.render(),
    )

    # TODO: fix images / media
    # if blog_mode == BlogMode.LOCAL:
    #     post_html = post_html.replace("/images/", str(output_path) + "/images/")

    return post_html
