class Tag:
    def __init__(self, name: str | int, color: str) -> None:
        self.name = str(name)
        self.color = color
        self.id = self.name.replace(" ", "").lower()

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, o: object) -> bool:
        return self.name == o.name and self.color == o.color

    def lower(self):
        return self.name.lower()

    def __repr__(self) -> str:
        return f"Tag(name={self.name}, color={self.color})"

    def __lt__(self, other):
        return self.name < other.name

    def __gt__(self, other):
        return self.name > other.name

    def __le__(self, other):
        return self.name <= other.name

    def __ge__(self, other):
        return self.name >= other.name

    def to_json(self):
        return {
            "name": self.name,
            "color": self.color,
            "id": self.id,
        }

    @classmethod
    def from_json(cls, data):
        return cls(
            name=data["name"],
            color=data["color"],
        )
