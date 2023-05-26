from typing import List, Set

from blogger.core import *
from blogger.templates import *
from blogger.utils import *


class BlogIndex:
    def __init__(self) -> None:
        self.posts: List[BlogPost] = []
        self.tags: Set[Tag] = set()

    def sort_posts(self):
        self.posts.sort(key=lambda post: post.date, reverse=True)

    # def sorted_tags(self, tags: Set[Tag]) -> Set[Tag]:
    #     return set(sorted(list(tags), key=lambda tag: tag.lower()))

    def archived_posts(self) -> List[BlogPost]:
        return [post for post in self.posts if post.archived]

    def non_archived_posts(self) -> List[BlogPost]:
        return [post for post in self.posts if not post.archived]

    def add_post(self, post: BlogPost):
        self.posts.append(post)
        self.tags.update(post.tags)

    def _render_index(self, output_path: Path, blog_mode: BlogMode) -> str:
        archived_posts = self.archived_posts()
        non_archived_posts = self.non_archived_posts()

        post_list = BlogPostList(non_archived_posts).render(output_path, blog_mode)
        archived_post_list = BlogPostList(archived_posts).render(output_path, blog_mode)

        self.tags = sorted(list(self.tags), key=lambda tag: tag.lower())
        year_tags = set()
        for post in self.posts:
            year_tags.add(
                Tag(
                    name=str(post.date.year),
                    link=f"year/{post.date.year}.html",
                    color="tag-year",
                )
            )
        self.tags.extend(sorted(list(year_tags)))

        return Templates.index().render(
            recent_count=len(non_archived_posts),
            archived_count=len(archived_posts),
            post_list=post_list,
            archived_post_list=archived_post_list,
            all_tags_list=TagList(self.tags).render(output_path, blog_mode),
            header=Header().render(blog_mode, output_path),
        )

    def save_index(self, blog_mode: BlogMode, output_path: Path):
        index_html = self._render_index(output_path, blog_mode)
        with open(output_path / "index.html", "w") as f:
            f.write(index_html)
