import json
import os
import re
from models.deck import Deck
from models.card import Card

DATA_DIR = "flashcards"

class DeckManager:
    MAX_FILENAME_LENGTH = 50  # Maximum length for deck names

    def __init__(self):
        self.decks = {}
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensures that the data and import directories exist."""
        os.makedirs(DATA_DIR, exist_ok=True)

    def _sanitize_filename(self, name):
        """Sanitizes and validates the filename."""
        safe_name = name.strip()
        safe_name = re.sub(r'[<>:"/\\|?*\n\r\t]', '_', safe_name)
        safe_name = re.sub(r'\s+', '_', safe_name)  # Replace whitespace with underscore
        safe_name = re.sub(r'_+', '_', safe_name)   # Replace multiple underscores with single
        safe_name = safe_name.strip('._-')          # Remove leading/trailing special chars
        
        # ensure we have a valid filename
        if not safe_name:
            safe_name = "unnamed_deck"
            
        # truncate if too long (leaving room for .json extension)
        if len(safe_name) > self.MAX_FILENAME_LENGTH:
            safe_name = safe_name[:self.MAX_FILENAME_LENGTH]
            safe_name = safe_name.rstrip('._-')  # remove any partial/trailing special chars
            
        return safe_name

    def _deck_filepath(self, deck_name):
        """Returns the file path for a given deck name."""
        safe_name = self._sanitize_filename(deck_name)
        if not safe_name:
            raise ValueError("Invalid deck name")
        return os.path.join(DATA_DIR, f"{safe_name}.json")

    def _load_deck(self, deck_name):
        """Loads a deck from its individual file."""
        filepath = self._deck_filepath(deck_name)
        try:
            with open(filepath, 'r') as f:
                deck_data = json.load(f)
                return Deck.from_dict(deck_data)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
        except Exception as e:
            print(f"Error loading deck {deck_name}: {e}")
            return None

    def _save_deck(self, deck):
        """Saves a deck to its individual file."""
        try:
            filepath = self._deck_filepath(deck.name)
            with open(filepath, 'w') as f:
                json.dump(deck.to_dict(), f, indent=4)
        except Exception as e:
            raise Exception(f"Error saving deck: {e}")

    def get_deck(self, name, load_if_not_found=True):
        """Gets a deck, loading it if necessary."""
        if name not in self.decks and load_if_not_found:
            self.decks[name] = self._load_deck(name)
        return self.decks.get(name)

    def get_all_deck_names(self):
        """Returns a list of all available deck names."""
        deck_names = []
        try:
            for filename in os.listdir(DATA_DIR):
                if filename.endswith(".json"):
                    deck_name = filename[:-5]  # remove ".json" extension
                    if deck_name not in self.decks:
                        deck = self._load_deck(deck_name)
                        if deck:
                            self.decks[deck_name] = deck
                    deck_names.append(deck_name)
        except Exception as e:
            print(f"Error listing decks: {e}")
        return deck_names

    def create_deck(self, name):
        """Creates a new deck."""
        # Validate name length
        if not name or len(name) > self.MAX_FILENAME_LENGTH:
            raise ValueError(f"Deck name must be between 1 and {self.MAX_FILENAME_LENGTH} characters")

        safe_name = self._sanitize_filename(name)
        if safe_name in self.get_all_deck_names():
            return False

        try:
            self.decks[safe_name] = Deck(safe_name)
            self._save_deck(self.decks[safe_name])
            return True
        except Exception:
            if safe_name in self.decks:
                del self.decks[safe_name]
            raise

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
        # Validate new name length
        if not new_name or len(new_name) > self.MAX_FILENAME_LENGTH:
            raise ValueError(f"New deck name must be between 1 and {self.MAX_FILENAME_LENGTH} characters")

        safe_new_name = self._sanitize_filename(new_name)
        if old_name in self.get_all_deck_names() and safe_new_name not in self.get_all_deck_names():
            old_filepath = self._deck_filepath(old_name)
            new_filepath = self._deck_filepath(safe_new_name)
            try:
                os.rename(old_filepath, new_filepath)
                if old_name in self.decks:
                    self.decks[safe_new_name] = self.decks.pop(old_name)
                    self.decks[safe_new_name].name = safe_new_name
                return True
            except Exception as e:
                print(f"Error renaming deck file: {e}")
                return False
        return False