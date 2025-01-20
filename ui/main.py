import curses
from .base import BaseUI
from .deck_actions import DeckActions
from models.deck_manager import DeckManager

class TUI(BaseUI):
    """Main TUI class orchestrating the flashcard application."""
    def __init__(self, stdscr, input_handler):
        super().__init__(stdscr)
        self.deck_manager = DeckManager()
        self.input_handler = input_handler
        self.deck_actions = DeckActions(stdscr, self.deck_manager, input_handler)

    def run(self):
        while True:
            try:
                choice = self.input_handler.show_menu(
                    "flash",
                    [
                        ("1", "Create Deck"),
                        ("2", "Select Deck"),
                        ("3", "Exit")
                    ]
                )
                if choice == '3':
                    break
                self._run_action(choice)
            except KeyboardInterrupt:
                break

    def _run_action(self, choice):
        actions = {
            '1': self.deck_actions.create_deck_menu,
            '2': self.deck_actions.select_deck_menu,
        }
        if choice in actions:
            actions[choice]()