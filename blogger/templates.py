from functools import cache
from pathlib import Path

from blogger.utils import *


def read_template(name: str):
    return open(f"templates/{name}.html", "r").read()


class Template:
    def __init__(self, template_name) -> None:
        self._template = read_template(template_name)

    def render(self, **kwargs):
        return self._template.format(**kwargs)


class Templates:
    @staticmethod
    @cache
    def post():
        return Template("post")

    @staticmethod
    @cache
    def index():
        return Template("index")

    @staticmethod
    @cache
    def tag():
        return Template("tag")

    @staticmethod
    @cache
    def meta():
        return Template("meta")

    @staticmethod
    @cache
    def header():
        return Template("header")

    @staticmethod
    @cache
    def post_list_entry():
        return Template("post_list_entry")

    @staticmethod
    @cache
    def tag_page():
        return Template("tag_page")


class Header:
    @staticmethod
    def render(mode: BlogMode, output: Path):
        if mode == BlogMode.WEB:
            return Templates.header().render(home_link="/")
        else:
            return Templates.header().render(home_link=str(output) + "/index.html")
