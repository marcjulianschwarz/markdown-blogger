import json
import shutil
from pathlib import Path
from typing import List, Set

from blogger.blogpost import BlogPost
from blogger.tag import Tag


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
        """Sort post by date or title"""
        if by == "date":
            self.posts.sort(key=lambda post: post.date, reverse=True)
        elif by == "title":
            self.posts.sort(key=lambda post: post.title, reverse=True)
        else:
            raise ValueError(f"Unknown sort key: {by}")

    def add_post(self, post: BlogPost):
        # update post in post list if it already exists
        for i, p in enumerate(self.posts):
            if p.id == post.id:
                self.posts[i] = post
                break
        # otherwise add it as a new one
        else:
            self.posts.append(post)

        # update tags with the tags from the new post
        for tag in post.tags:
            self.tags.discard(tag)  # Remove tag if present, do nothing otherwise
            self.tags.add(tag)  # Add updated tag (if not present)

    def remove_post(self, post: BlogPost, posts_path: Path):
        for i, p in enumerate(self.posts):
            if p.id == post.id:
                self.posts.pop(i)
                if (posts_path / post.html_path).exists():
                    print(f"Removing unused post: {post.title}")
                    shutil.rmtree(posts_path / post.html_path)
                break

    def remove_unused_tags(self, tags_path: Path, post: BlogPost):
        # remove tags that are no longer used
        for tag in post.tags:
            if not any(tag in post.tags for post in self.posts):
                print(tag.name)
                self.tags.discard(tag)
                if (tags_path / f"{tag.id}").exists():
                    print(f"Removing unused tag: {tag.name}")
                    shutil.rmtree(tags_path / f"{tag.id}")

    def _to_json(self):
        return json.dumps(
            {
                "posts": [post.to_json() for post in self.posts],
                "tags": [tag.to_json() for tag in self.tags],
            }
        )

    def post_in_index(self, post: BlogPost) -> bool:
        return any(p.id == post.id for p in self.posts)

    def to_json(self):
        self.blog_index_path.write_text(self._to_json())

    def not_modified(self, post: BlogPost) -> bool:
        """Checks if the post has been modified since the last build."""
        if not self.blog_index_path.exists():
            return False

        with open(self.blog_index_path, "r") as f:
            data = json.load(f)

        for p in data["posts"]:
            if p["id"] == post.id:
                return p["last_modified"] == post.last_modified.strftime("%Y-%m-%d")

        return False
