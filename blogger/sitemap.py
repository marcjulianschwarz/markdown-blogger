from pathlib import Path
from xml.dom.minidom import Document


class Sitemap:
    def __init__(self) -> None:
        self.doc = Document()
        self.base = self.doc.createElement("urlset")
        self.base.setAttribute("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
        self.doc.appendChild(self.base)

    def update_sitemap(self, url: str, lastmod: str):
        child_url = self.doc.createElement("url")
        child_loc = self.doc.createElement("loc")
        child_loc.appendChild(self.doc.createTextNode(url))
        child_lastmod = self.doc.createElement("lastmod")
        child_lastmod.appendChild(self.doc.createTextNode(lastmod))
        child_url.appendChild(child_loc)
        child_url.appendChild(child_lastmod)
        self.base.appendChild(child_url)

    def save_sitemap(self, output: Path):
        xml = self.doc.toxml()
        with open(output / "sitemap.xml", "w") as f:
            f.write(xml)
