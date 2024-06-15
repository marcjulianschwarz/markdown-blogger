from pathlib import Path

import yaml


class BlogConfig:
    blog_in_path: Path
    blog_out_path: Path
    tags_path: Path
    blog_index_path: Path
    posts_path: Path
    force_update: bool = False
    media_path: Path = Path("media")

    def __init__(self, yaml: dict) -> None:
        self.yaml = yaml
        self.blog_in_path = Path(yaml["blog_in_path"])
        self.blog_out_path = Path(yaml["blog_out_path"])
        self.tags_path = Path(yaml["tags_path"])
        self.blog_index_path = Path(yaml["blog_index_path"])
        self.posts_path = Path(yaml["posts_path"])

        if "force_update" in yaml:
            self.force_update = yaml["force_update"]

        if "media_path" in yaml:
            self.media_path = Path(yaml["media_path"])

    @classmethod
    def from_yaml(cls, path: str | Path):
        path = Path(path)
        if path.exists():
            config = yaml.load(path.read_text(), Loader=yaml.FullLoader)
        return cls(config)

    @classmethod
    def from_dict(cls, dict: dict):
        return cls(dict)
