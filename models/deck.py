import random
from models.card import Card

class Deck:
    def __init__(self, name: str, cards=None):
        self.name = name
        self.cards = cards or []

    def add_card(self, card):
        self.cards.append(card)

    def remove_card(self, index):
        if 0 <= index < len(self.cards):
            del self.cards[index]

    def edit_card(self, index: int, front=None, back=None):
        if 0 <= index < len(self.cards):
            if front is not None:
                self.cards[index].front = front
            if back is not None:
                self.cards[index].back = back

    def shuffle(self):
        random.shuffle(self.cards)

    def to_dict(self):
        return {"name": self.name, "cards": [c.to_dict() for c in self.cards]}

    @classmethod
    def from_dict(cls, data):
        return cls(data["name"], [Card.from_dict(c) for c in data.get("cards", [])])