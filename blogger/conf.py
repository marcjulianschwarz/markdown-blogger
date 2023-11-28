from pathlib import Path

import yaml


class BlogConfig:
    blog_in_path: Path
    blog_out_path: Path
    tags_path: Path
    blog_index_path: Path

    def __init__(self, yaml) -> None:
        self.yaml = yaml
        self.blog_in_path = Path(yaml["blog_in_path"])
        self.blog_out_path = Path(yaml["blog_out_path"])
        self.tags_path = Path(yaml["tags_path"])
        self.blog_index_path = Path(yaml["blog_index_path"])

    @classmethod
    def from_yaml(cls, path: str | Path):
        path = Path(path)
        if path.exists():
            config = yaml.load(path.read_text(), Loader=yaml.FullLoader)
        return cls(config)

    @classmethod
    def from_dict(cls, dict: dict):
        return cls(dict)
