from typing import List

from blogger.core import BlogPost, Tag
from blogger.templates import Header, Templates


def _valid_tag_name(tag_name: str) -> bool:
    return tag_name != "" and tag_name != "blog"


def render_tag_list(tags: List[Tag]) -> str:
    tags_html = ""
    for tag in tags:
        if tag and _valid_tag_name(tag.name):
            tags_html += Templates.tag().render(
                name=str(tag.name), link="/" + tag.path, color_class=tag.color
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


def render_tag_page(self) -> str:
    post_list = render_blog_list(self.posts)
    return Templates.tag_page().render(
        name=self.tag.name,
        count=len(self.posts),
        post_list=post_list,
        header=Header().render(),
    )
