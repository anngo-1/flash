import curses
from .base import BaseUI
from .input_handler import InputHandler
from .card_display import CardDisplay
from models.card import Card

class DeckActions(BaseUI):
    """Handles deck-related actions and menus."""
    def __init__(self, stdscr, deck_manager):
        super().__init__(stdscr)
        self.deck_manager = deck_manager
        self.input_handler = InputHandler(stdscr)
        self.card_display = CardDisplay(stdscr, self.input_handler)  
        self.card_display.deck_manager = deck_manager 

    def create_deck_menu(self):
        """Handle the creation of a new deck."""
        deck_name = self.input_handler.get_multiline_input("Enter deck name:")
        if deck_name:
            if self.deck_manager.create_deck(deck_name):
                self.display_message(f"Deck '{deck_name}' created!", pause=True)
            else:
                self.display_message(f"Deck '{deck_name}' already exists.", pause=True)
        else:
            self.display_message("Cancelled.", pause=True)

    def select_deck_menu(self):
        """Display a menu to select a deck."""
        decks = sorted(self.deck_manager.get_all_deck_names())
        if not decks:
            self.display_message("No decks available.", pause=True)
            return

        options = [
            (str(i + 1), name) for i, name in enumerate(decks)
        ] + [("0", "Back")]

        choice = self.input_handler.show_menu("Select Deck", options)
        if choice and choice != '0':
            try:
                selected_deck = self.deck_manager.get_deck(decks[int(choice) - 1])
                self.deck_actions_menu(selected_deck)
            except ValueError:
                self.display_message("Invalid selection.", pause=True)

    def deck_actions_menu(self, deck):
        """Display the actions available for a selected deck."""
        while True:
            choice = self.input_handler.show_menu(
                f"Deck: {deck.name}",
                [
                    ("1", "Add Card"),
                    ("2", "Edit Card"),
                    ("3", "Delete Card"),
                    ("4", "Study Deck"),
                    ("5", "Rename Deck"),
                    ("6", "Delete Deck"),
                    ("7", "Back")
                ]
            )

            if not choice or choice == '7':
                break

            actions = {
                '1': self.add_card_menu,
                '2': self.edit_card_menu,
                '3': self.delete_card_menu,
                '4': self.card_display.study_deck,
                '5': self.rename_deck_menu,
                '6': self.delete_deck_confirmation
            }

            action = actions.get(choice)
            if action:
                if choice == '6':
                    if action(deck):  # if deck was successfully deleted
                        break  # go back to the main menu
                else:
                    action(deck)

    def add_card_menu(self, deck):
        """Handle the process of adding a card to the current deck."""
        front_text = self.input_handler.get_multiline_input("Enter card front:")
        if front_text:
            back_text = self.input_handler.get_multiline_input("Enter card back:")
            if back_text:
                deck.add_card(Card(front_text, back_text))
                try:
                    self.deck_manager._save_deck(deck)
                    self.display_message("Card added!", pause=True)
                except Exception as e:
                    self.display_message(f"Error saving deck: {e}", pause=True)

    def edit_card_menu(self, deck):
        """Handle the process of editing an existing card in the deck."""
        if not deck.cards:
            self.display_message("No cards in this deck.", pause=True)
            return

        options = [
            (str(i + 1), f"Front: {c.front[:40].replace('\n', ' ')}...")
            for i, c in enumerate(deck.cards)
        ] + [("0", "Cancel")]

        choice = self.input_handler.show_menu("Edit Card", options)
        if choice and choice != '0':
            try:
                card_to_edit = deck.cards[int(choice) - 1]
                
                new_front = self.input_handler.get_multiline_input(
                    f"Current front:\n{card_to_edit.front}\nNew front (empty to keep):",
                    card_to_edit.front
                )
                if new_front is not None:
                    card_to_edit.front = new_front

                new_back = self.input_handler.get_multiline_input(
                    f"Current back:\n{card_to_edit.back}\nNew back (empty to keep):",
                    card_to_edit.back
                )
                if new_back is not None:
                    card_to_edit.back = new_back

                self.deck_manager._save_deck(deck)
                self.display_message("Card updated.", pause=True)
            except ValueError:
                self.display_message("Invalid selection.", pause=True)

    def delete_card_menu(self, deck):
        """Handle the process of deleting a card from the deck."""
        if not deck.cards:
            self.display_message("No cards in this deck.", pause=True)
            return

        options = [
            (str(i + 1), f"Front: {c.front[:40].replace('\n', ' ')}...")
            for i, c in enumerate(deck.cards)
        ] + [("0", "Cancel")]

        choice = self.input_handler.show_menu("Delete Card", options)
        if choice and choice != '0':
            try:
                deck.remove_card(int(choice) - 1)
                self.deck_manager._save_deck(deck)
                self.display_message("Card deleted.", pause=True)
            except ValueError:
                self.display_message("Invalid selection.", pause=True)

    def rename_deck_menu(self, deck):
        """Handle the process of renaming the current deck."""
        new_name = self.input_handler.get_multiline_input(
            f"Enter new name for '{deck.name}':"
        )
        if new_name and self.deck_manager.rename_deck(deck.name, new_name):
            self.display_message(f"Deck renamed to '{new_name}'.", pause=True)
            deck.name = new_name
        else:
            self.display_message(
                "Could not rename deck (name might be taken).",
                pause=True
            )

    def delete_deck_confirmation(self, deck):
        """Ask for confirmation before deleting a deck."""
        choice = self.input_handler.show_menu(
            f"Delete: {deck.name}?",
            [("y", "Yes"), ("n", "No")]
        )
        
        if choice == 'y':
            if self.deck_manager.delete_deck(deck.name):
                self.display_message("Deck deleted.", pause=True)
                return True
            else:
                self.display_message("Error deleting deck.", pause=True)
        else:
            self.display_message("Deletion cancelled.", pause=True)
        return False