class Card:
    def __init__(self, front: str, back: str):
        self.front = front
        self.back = back

    def to_dict(self):
        return {"front": self.front, "back": self.back}

    @classmethod
    def from_dict(cls, data):
        return cls(data["front"], data["back"])