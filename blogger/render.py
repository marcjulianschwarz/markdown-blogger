from typing import List

from blogger import markdown2
from blogger.blog_index import BlogIndex
from blogger.blogpost import BlogPost
from blogger.conf import BlogConfig
from blogger.tag import Tag
from blogger.templates import Header, Templates
from blogger.utils import MARKDOWN_EXTRAS


def _valid_tag_name(tag_name: str) -> bool:
    return tag_name != "" and tag_name != "blog"


def render_tag_list(tags: List[Tag], config: BlogConfig) -> str:
    tags_html = ""
    for tag in tags:
        if tag and _valid_tag_name(tag.name):
            tags_html += Templates.tag().render(
                name=str(tag.name),
                link=f"/blog/{config.tags_path}/{tag.id}.html",
                color_class=tag.color,
            )
    return tags_html


def render_blog_list(posts: List[BlogPost], config: BlogConfig) -> str:
    post_list = ""
    for post in posts:
        post_entry = Templates.post_list_entry().render(
            title=post.title,
            subtitle=post.subtitle,
            author=post.author,
            date=post.date.strftime("%d.%m.%Y"),
            link=f"/blog/{config.posts_path / post.html_path}",
        )
        post_list += post_entry
    return post_list


def render_tag_page(tag: Tag, posts: List[BlogPost], config: BlogConfig) -> str:
    posts = sorted(posts, key=lambda x: x.date, reverse=True)
    post_list = render_blog_list(posts, config)
    return Templates.tag_page().render(
        name=tag.name,
        count=len(posts),
        post_list=post_list,
        header=Header().render(),
    )


def render_blog_post(post: BlogPost, config: BlogConfig) -> str:
    html = markdown2.markdown(
        post.content,
        extras=MARKDOWN_EXTRAS,
    )

    html = html.replace('src="/images/', f'src="/blog/{config.media_path}/')

    tag_list = render_tag_list(post.tags, config=config)

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

    return post_html


def render_index(blog_index: BlogIndex, config: BlogConfig) -> str:
    archived_posts = [post for post in blog_index.posts if post.archived]
    non_archived_posts = [post for post in blog_index.posts if not post.archived]

    non_archived_posts = sorted(non_archived_posts, key=lambda x: x.date, reverse=True)
    archived_posts = sorted(archived_posts, key=lambda x: x.date, reverse=True)

    post_list = render_blog_list(non_archived_posts, config)
    archived_post_list = render_blog_list(archived_posts, config)

    tags = sorted(list(blog_index.tags), key=lambda tag: tag.lower())
    tag_list = render_tag_list(tags, config)

    return Templates.index().render(
        recent_count=len(non_archived_posts),
        archived_count=len(archived_posts),
        post_list=post_list,
        archived_post_list=archived_post_list,
        all_tags_list=tag_list,
        header=Header().render(),
    )
