import json
from datetime import datetime as dt
from pathlib import Path
from typing import List, Set

from blogger.blogpost import BlogPost
from blogger.constants import YEARS_PATH
from blogger.render import render_blog_list, render_tag_list
from blogger.tag import Tag
from blogger.templates import Header, Templates


class BlogIndex:
    def __init__(self, blog_index_path: Path) -> None:
        """Stores all blog posts and tags."""
        self.posts: List[BlogPost] = []
        self.tags: Set[Tag] = set()
        self.blog_index_path = blog_index_path

    @classmethod
    def from_json(cls, path: Path):
        blog_index = cls(path)
        data = json.loads(path.read_text())
        blog_index.posts = [BlogPost.from_json(post) for post in data["posts"]]
        blog_index.tags = {Tag.from_json(tag) for tag in data["tags"]}
        return blog_index

    def sort_posts(self, by: str = "date"):
        if by == "date":
            self.posts.sort(key=lambda post: post.date, reverse=True)
        elif by == "title":
            self.posts.sort(key=lambda post: post.title, reverse=True)
        else:
            raise ValueError(f"Unknown sort key: {by}")

    def add_post(self, post: BlogPost):
        # update post in post list if it already exists
        for i, p in enumerate(self.posts):
            if p.path == post.path:
                self.posts[i] = post
                return
        else:
            self.posts.append(post)

        for tag in post.tags:
            for i, t in enumerate(self.tags):
                if t.name == tag.name:
                    self.tags[i] = tag
                    break
            else:
                self.tags.add(tag)

    def _render_index(self) -> str:
        archived_posts = [post for post in self.posts if post.archived]
        non_archived_posts = [post for post in self.posts if not post.archived]

        post_list = render_blog_list(non_archived_posts)
        archived_post_list = render_blog_list(archived_posts)

        self.tags = sorted(list(self.tags), key=lambda tag: tag.lower())

        # add years to the end of the tag list
        # year_tags = self._create_year_tags()
        # self.tags.extend(sorted(list(year_tags)))

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
                    path=YEARS_PATH,
                    color="tag-year",
                )
            )
        return year_tags

    def save_index(self, output_path: Path):
        index_html = self._render_index()
        (output_path / "index.html").write_text(index_html)

    def _to_json(self):
        return json.dumps(
            {
                "posts": [post.to_json() for post in self.posts],
                "tags": [tag.to_json() for tag in self.tags],
            }
        )

    def to_json(self):
        self.blog_index_path.write_text(self._to_json())

    def not_modified(self, file: Path) -> bool:
        """Checks if the post has been modified since the last build."""
        if not self.blog_index_path.exists():
            return False

        with open(self.blog_index_path, "r") as f:
            data = json.load(f)

        for post in data["posts"]:
            if post["path"] == str(file):
                return post["last_modified"] == dt.fromtimestamp(
                    file.stat().st_mtime
                ).strftime("%Y-%m-%d")

        return False
