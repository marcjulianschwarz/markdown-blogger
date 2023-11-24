class Tag:
    def __init__(self, name: str | int, path: str, color: str) -> None:
        self.name = str(name)
        self.path = path
        self.color = color

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, o: object) -> bool:
        return self.name == o.name and self.path == o.path and self.color == o.color

    def lower(self):
        return self.name.lower()

    def __repr__(self) -> str:
        return f"Tag(name={self.name}, path={self.path}, color={self.color})"

    def __lt__(self, other):
        return self.name < other.name

    def __gt__(self, other):
        return self.name > other.name

    def __le__(self, other):
        return self.name <= other.name

    def __ge__(self, other):
        return self.name >= other.name
