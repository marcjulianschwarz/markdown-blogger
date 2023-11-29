import socket
import socketserver
import urllib.parse
import webbrowser

import frontmatter
from tqdm import tqdm

from blogger.blog_index import BlogIndex
from blogger.blogpost import BlogPost
from blogger.conf import BlogConfig
from blogger.render import render_blog_post, render_index, render_tag_page
from blogger.sitemap import Sitemap
from blogger.utils import create_http_handler, is_skip


class Blog:
    def __init__(
        self,
        markdown_path: str | None = None,
        output_path: str | None = None,
        config: BlogConfig | None = None,
    ):
        # Initialize config
        if not config:
            if not markdown_path or not output_path:
                raise ValueError(
                    "You need to either provide a config or markdown and output path."
                )
            config = BlogConfig.from_dict(
                {"blog_in_path": markdown_path, "blog_out_path": output_path}
            )
        self.config = config

        # Initialize blog index and sitemap file
        if config.blog_index_path.exists():
            self.blog_index = BlogIndex.from_json(config.blog_index_path)
        else:
            self.blog_index = BlogIndex(config.blog_index_path)
        self.sitemap = Sitemap()

    def build_index_and_create_posts(self):
        """
        Builds the blog index and updates the sitemap file.
        1. Read markdown file from markdown path
        2. Load metadata from frontmatter and file object
        3. Check if post should be skipped
        4. Create BlogPost object
        5. Add post to blog index
        6. Update sitemap
        7. Save post
        """
        markdown_files = list(self.config.blog_in_path.glob("*.md"))
        self.log(str(len(markdown_files)), "FILES")

        posts_path = self.config.blog_out_path / self.config.posts_path
        tags_path = self.config.blog_out_path / self.config.tags_path
        posts_path.mkdir(parents=True, exist_ok=True)
        tags_path.mkdir(parents=True, exist_ok=True)

        for file in markdown_files:
            file_content = file.read_text()
            post_meta = frontmatter.loads(file_content)
            post = BlogPost(post_meta, file)

            if not self.config.force_update:
                if is_skip(post_meta):
                    self.log(file.name, "SKIP")
                    self.blog_index.remove_post(post, posts_path)
                    self.blog_index.remove_unused_tags(tags_path)
                    continue
                if self.blog_index.not_modified(post) and self.blog_index.post_in_index(
                    post
                ):
                    self.log(file.name, "NOMOD")
                    continue

            self.log(file.name, "POST")

            post_html = render_blog_post(post, self.config)
            (posts_path / post.html_path).write_text(post_html)

            self.blog_index.add_post(post)
            self.sitemap.update_sitemap(
                url=f"https://www.marc-julian.de/posts/{str(post.date.year)}/{str(post.date.month)}/{urllib.parse.quote(file.stem)}.html",
                lastmod=post.last_modified.strftime("%Y-%m-%d"),
            )

    def create_tag_pages(self):
        for tag in self.blog_index.tags:
            posts = [
                post
                for post in self.blog_index.posts
                if tag in post.tags
                or post.date.year == (tag.name.isnumeric() and int(tag.name))
            ]

            tag_page = render_tag_page(tag, posts, self.config)
            (
                self.config.blog_out_path / self.config.tags_path / f"{tag.id}.html"
            ).write_text(tag_page)

    def create_index(self):
        index_html = render_index(self.blog_index, self.config)
        (self.config.blog_out_path / "index.html").write_text(index_html)

    def create_sitemap(self):
        self.sitemap.save_sitemap(self.config.blog_out_path)

    def open_blog(self):
        # start http server at output path
        handler = create_http_handler(self.config.blog_out_path)
        httpd = None

        try:
            with MyTCPServer(("", 8000), handler) as httpd:
                httpd.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                print("serving at port", 8000)
                webbrowser.open("http://localhost:8000")
                httpd.serve_forever()
        except KeyboardInterrupt:
            print("Stopping server...")
        if httpd:
            httpd.shutdown()

    def log(self, message: str, modifier: str = "MESSAGE"):
        padding = max(0, 20 - len(modifier))
        print(f"[{modifier}]{' ' * padding}{message}")


class MyTCPServer(socketserver.TCPServer):
    allow_reuse_address = True
