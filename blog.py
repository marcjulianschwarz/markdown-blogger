from blogger.blog import Blog
from blogger.utils import BlogMode
from argparse import ArgumentParser
from paths import BLOG_IN, BLOG_OUT

parser = ArgumentParser()
parser.add_argument("-w", "--web", action="store_true")
parser.add_argument("-l", "--local", action="store_true")
parser.add_argument(
    "-d", "--show_demo", type=bool, default=False, choices=[True, False]
)
parser.add_argument(
    "-o",
    "--open",
    type=bool,
    default=False,
    choices=[True, False],
    const=True,
    nargs="?",
)

args = parser.parse_args()


blog = Blog(
    BLOG_IN,
    BLOG_OUT,
    mode=BlogMode.WEB if args.web else BlogMode.LOCAL,
    show_demo=args.show_demo,
)

blog.delete_output()
blog.build_index_and_create_posts()
blog.create_index()
blog.create_tag_pages()
blog.create_sitemap()

if args.open:
    blog.open_index()
