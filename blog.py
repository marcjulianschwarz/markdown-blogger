from argparse import ArgumentParser

from blogger.blog import Blog
from blogger.conf import BlogConfig

parser = ArgumentParser()
parser.add_argument("action", choices=["update", "show"])
args = parser.parse_args()


config = BlogConfig.from_yaml("conf.yaml")
blog = Blog(config=config)

if args.action == "update":
    blog.build_index_and_create_posts()

    blog.create_index()
    blog.create_tag_pages()
    blog.create_recent_posts()
    blog.create_sitemap()
    blog.create_rss_feed()

    blog.blog_index.to_json()


elif args.action == "show":
    blog.open_blog()

else:
    print("Please provide either 'update' or 'show' as an argument.")
