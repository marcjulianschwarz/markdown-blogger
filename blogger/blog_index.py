from pathlib import Path
from typing import List, Set

from blogger.blogpost import BlogPost
from blogger.constants import YEARS_PATH
from blogger.render import render_blog_list, render_tag_list
from blogger.tag import Tag
from blogger.templates import Header, Templates


class BlogIndex:
    def __init__(self) -> None:
        """Stores all blog posts and tags."""
        self.posts: List[BlogPost] = []
        self.tags: Set[Tag] = set()

    def sort_posts(self, by: str = "date"):
        if by == "date":
            self.posts.sort(key=lambda post: post.date, reverse=True)
        elif by == "title":
            self.posts.sort(key=lambda post: post.title, reverse=True)
        else:
            raise ValueError(f"Unknown sort key: {by}")

    def add_post(self, post: BlogPost):
        self.posts.append(post)
        self.tags.update(post.tags)

    def _render_index(self) -> str:
        archived_posts = [post for post in self.posts if post.archived]
        non_archived_posts = [post for post in self.posts if not post.archived]

        post_list = render_blog_list(non_archived_posts)
        archived_post_list = render_blog_list(archived_posts)

        self.tags = sorted(list(self.tags), key=lambda tag: tag.lower())

        # add years to the end of the tag list
        #year_tags = self._create_year_tags()
        #self.tags.extend(sorted(list(year_tags)))

        return Templates.index().render(
            recent_count=len(non_archived_posts),
            archived_count=len(archived_posts),
            post_list=post_list,
            archived_post_list=archived_post_list,
            all_tags_list=render_tag_list(self.tags),
            header=Header().render(),
        )

    def _create_year_tags(self) -> Set[Tag]:
        """Creates a set of year tags from the posts publish dates."""
        year_tags = set()
        for post in self.posts:
            year_tags.add(
                Tag(
                    name=str(post.date.year),
                    path=f"/{YEARS_PATH}/{post.date.year}.html",
                    color="tag-year",
                )
            )
        return year_tags

    def save_index(self, output_path: Path):
        index_html = self._render_index()
        (output_path / "index.html").write_text(index_html)
