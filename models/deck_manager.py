import json
import os
from models.deck import Deck
from models.card import Card

DATA_DIR = "flashcards"

class DeckManager:
    def __init__(self):
        self.decks = {}  
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensures that the data and import directories exist."""
        os.makedirs(DATA_DIR, exist_ok=True)

    def _deck_filepath(self, deck_name):
        """Returns the file path for a given deck name."""
        safe_filename = "".join(c if c.isalnum() or c in "._-" else "_" for c in deck_name) + ".json"
        return os.path.join(DATA_DIR, safe_filename)

    def _load_deck(self, deck_name):
        """Loads a deck from its individual file."""
        filepath = self._deck_filepath(deck_name)
        try:
            with open(filepath, 'r') as f:
                deck_data = json.load(f)
                return Deck.from_dict(deck_data)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def _save_deck(self, deck):
        """Saves a deck to its individual file."""
        filepath = self._deck_filepath(deck.name)
        try:
            with open(filepath, 'w') as f:
                json.dump(deck.to_dict(), f, indent=4)
        except (IOError, TypeError) as e:
            raise Exception(f"Error saving deck: {e}")

    def get_deck(self, name, load_if_not_found=True):
        """Gets a deck, loading it if necessary."""
        if name not in self.decks and load_if_not_found:
            self.decks[name] = self._load_deck(name)
        return self.decks.get(name)

    def get_all_deck_names(self):
        """Returns a list of all available deck names."""
        deck_names = []
        for filename in os.listdir(DATA_DIR):
            if filename.endswith(".json"):
                deck_name = filename[:-5]  # remove ".json" extension
                # check if the deck is already loaded
                if deck_name not in self.decks:
                    # attempt to load and validate the deck
                    deck = self._load_deck(deck_name)
                    if deck:
                        self.decks[deck_name] = deck  # add to loaded decks
                        deck_names.append(deck_name)
                else:
                    deck_names.append(deck_name)
        return deck_names

    def create_deck(self, name):
        """Creates a new deck."""
        if name not in self.get_all_deck_names():
            self.decks[name] = Deck(name)
            self._save_deck(self.decks[name])
            return True
        return False

    def delete_deck(self, name):
        """Deletes a deck."""
        if name in self.get_all_deck_names():
            filepath = self._deck_filepath(name)
            try:
                os.remove(filepath)
                if name in self.decks:
                    del self.decks[name]
                return True
            except Exception as e:
                print(f"Error deleting deck file: {e}")
                return False
        return False

    def rename_deck(self, old_name, new_name):
        """Renames a deck."""
        if old_name in self.get_all_deck_names() and new_name not in self.get_all_deck_names():
            old_filepath = self._deck_filepath(old_name)
            new_filepath = self._deck_filepath(new_name)
            try:
                os.rename(old_filepath, new_filepath)
                if old_name in self.decks:
                    self.decks[new_name] = self.decks.pop(old_name)
                    self.decks[new_name].name = new_name
                return True
            except Exception as e:
                print(f"Error renaming deck file: {e}")
                return False
        return False

