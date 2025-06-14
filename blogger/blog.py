import socket
import socketserver
import webbrowser

import frontmatter

from blogger.blog_index import BlogIndex
from blogger.blogpost import BlogPost
from blogger.conf import BlogConfig
from blogger.render import (
    render_blog_list,
    render_blog_post,
    render_index,
    render_tag_page,
)
from blogger.sitemap import Sitemap
from blogger.utils import create_http_handler, is_skip
from feedgen.feed import FeedGenerator

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
        self.rss_generator = FeedGenerator()
        self.init_rss_feed()

    def init_rss_feed(self):
        self.rss_generator.id('https://marc-julian.com/blog')
        self.rss_generator.title('Marc Julian - Blog')
        self.rss_generator.author( {'name':'Marc Julian Schwarz'} )
        self.rss_generator.link( href='https://marc-julian.com/blog', rel='alternate' )
        # self.rssGenerator.logo('http://ex.com/logo.jpg')
        self.rss_generator.subtitle('This is a cool feed!')
        self.rss_generator.link( href='https://marc-julian.com/blog/rss.xml', rel='self' )
        self.rss_generator.language('en')

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
                    self.blog_index.remove_unused_tags(tags_path, post)
                    self.blog_index.remove_post(post, posts_path)
                    continue
                # if self.blog_index.not_modified(post) and self.blog_index.post_in_index(
                #     post
                # ):
                #     self.log(file.name, "NOMOD")
                #     continue

            self.log(file.name, "GENERATE POST")

            post_html = render_blog_post(post, self.config)
            html_path = posts_path / post.html_path
            if not html_path.exists():
                html_path.mkdir()
            (html_path / "index.html").write_text(post_html)

            self.blog_index.add_post(post)

            post_url = f"https://www.marc-julian.com/blog/{self.config.posts_path}/{post.html_path}"
            self.sitemap.update_sitemap(
                url=post_url,
                lastmod=post.last_modified.strftime("%Y-%m-%d"),
            )
            fe = self.rss_generator.add_entry()
            fe.id(post_url)
            fe.title(post.title)
            fe.link(href=post_url)

    def create_tag_pages(self):
        for tag in self.blog_index.tags:
            tagged_posts = [
                post
                for post in self.blog_index.posts
                if tag in post.tags
                or post.date.year == (tag.name.isnumeric() and int(tag.name))
            ]

            tag_page = render_tag_page(tag, tagged_posts, self.config)
            tag_folder = self.config.blog_out_path / self.config.tags_path / tag.id
            if not tag_folder.exists():
                tag_folder.mkdir()
            (tag_folder / "index.html").write_text(tag_page)

    def create_index(self):
        index_html = render_index(self.blog_index, self.config)
        (self.config.blog_out_path / "index.html").write_text(index_html)

    def create_recent_posts(self):
        posts = self.blog_index.posts
        non_archived_posts = filter(lambda post: not post.archived, posts)
        sorted_posts = sorted(
            non_archived_posts, key=lambda post: post.date, reverse=True
        )
        recent_posts = sorted_posts[:5]
        recent_posts_html = render_blog_list(recent_posts, self.config)
        (self.config.blog_out_path / "recent_posts.html").write_text(recent_posts_html)

    def create_sitemap(self):
        self.sitemap.save_sitemap(self.config.blog_out_path)

    def create_rss_feed(self):
        self.rss_generator.rss_file(self.config.blog_out_path / 'rss.xml')

    def open_blog(self):
        # start http server at output path
        handler = create_http_handler(self.config.blog_out_path)
        httpd = None

        try:
            with MyTCPServer(("", 8001), handler) as httpd:
                httpd.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                print("serving at port", 8001)
                webbrowser.open("http://localhost:8001")
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
