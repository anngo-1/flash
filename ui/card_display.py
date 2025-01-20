import curses
import textwrap
from collections import deque
import random
import time
from .base import BaseUI

class CardDisplay(BaseUI):
    """Handles card display and study functionality."""
    def __init__(self, stdscr, input_handler):
        super().__init__(stdscr)
        self.input_handler = input_handler
        self.deck_manager = None
        self.study_start_time = None
        self.current_mode = "standard"
        self.front_scroll_offset = 0  # for front card content
        self.back_scroll_offset = 0   # for back card content

    def _draw_text_in_box(self, r, c, h, w, text, color=None, scroll_offset=0):
        """Draw wrapped text within a specified box."""
        color = color or self.color_default
        wrapped_lines = [
            line for t in text.splitlines()
            for line in textwrap.wrap(t, width=max(1, w - 4))
        ]
        total_lines = len(wrapped_lines)
        available_lines = h - 2
        start_index = max(0, scroll_offset)
        end_index = min(total_lines, start_index + available_lines)

        for i, line in enumerate(wrapped_lines[start_index:end_index]):
            self.stdscr.addstr(
                r + 1 + i,
                c + 2,
                line,
                color
            )

        return total_lines

    def _show_card(self, card, current, total, deck_name, show_back=False, rating=None):
        """Display a flashcard."""
        rows, cols = self.stdscr.getmaxyx()
        card_width = min(cols - 6, 100)
        card_height = min(rows - 8, 18)
        start_row = (rows - card_height) // 2
        start_col = (cols - card_width) // 2

        self.stdscr.erase()

        # show deck info and progress
        title_text = f"Deck: {deck_name} ({current}/{total})"
        self.stdscr.addstr(
            1,
            max(0, (cols - len(title_text)) // 2),
            title_text,
            curses.A_BOLD | self.color_default
        )

        progress = f"Progress: "
        self.stdscr.addstr(3, 2, progress)
        progress_bar = "=" * int((current/total) * 20)
        self.stdscr.addstr(3, len(progress) + 2, f"[{progress_bar:<20}]")

        if self.current_mode == "timed" and self.study_start_time:
            elapsed = int(time.time() - self.study_start_time)
            timer_text = f"Time: {elapsed//60}m {elapsed%60}s"
            self.stdscr.addstr(3, cols - len(timer_text) - 2, timer_text)

        border_color = self.color_default
        if show_back and rating:
            border_color = {
                'got_it': self.color_correct,
                'aw_man': self.color_incorrect,
                'retry': self.color_progress
            }.get(rating, self.color_default)

        if not show_back:
            self._draw_box(
                start_row,
                start_col,
                card_height,
                card_width,
                "Front",
                border_color=self.color_default
            )
            total_lines = self._draw_text_in_box(
                start_row,
                start_col,
                card_height,
                card_width,
                card.front,
                scroll_offset=self.front_scroll_offset
            )
        else:
            box_height = (card_height - 1) // 2
            self._draw_box(
                start_row,
                start_col,
                box_height + 1,
                card_width,
                "Front",
                border_color=border_color
            )
            front_total_lines = self._draw_text_in_box(
                start_row,
                start_col,
                box_height + 1,
                card_width,
                card.front,
                scroll_offset=self.front_scroll_offset
            )

            self._draw_box(
                start_row + box_height + 1,
                start_col,
                box_height + 1,
                card_width,
                "Back",
                border_color=border_color
            )
            back_total_lines = self._draw_text_in_box(
                start_row + box_height + 1,
                start_col,
                box_height + 1,
                card_width,
                card.back,
                self.color_default,
                scroll_offset=self.back_scroll_offset
            )
            total_lines = back_total_lines

        if rows - 2 > 0:
            if not show_back:
                text = "Press <Space> or <Enter> to show back | Scroll: ↑/↓"
            else:
                text = "(1) I got it! (2) Aw man... (3) Retry | Top card: ↑/↓, Bottom card: j/k"
            
            self.stdscr.addstr(
                rows - 2,
                max(0, (cols - len(text)) // 2),
                text,
                curses.A_ITALIC | self.color_default
            )

        self.stdscr.refresh()
        return total_lines

    def study_deck(self, deck):
        """Handle deck study functionality."""
        if not deck.cards:
            self.display_message("No cards to study in this deck.", pause=True)
            return

        choice = self.input_handler.show_menu(
            f"Study: {deck.name}",
            [
                ("s", "Shuffle Deck"),
                ("t", "Timed Challenge (5min)"),
                ("c", "Continue Without Shuffling"),
                ("b", "Back")
            ]
        )

        if choice == 'b':
            return

        if choice == "s":
            deck.shuffle()
            self.deck_manager._save_deck(deck)
            self.display_message("Deck shuffled!", pause=False)
        elif choice == "t":
            self.current_mode = "timed"
            self.study_start_time = time.time()

        study_queue = deque(deck.cards)
        
        while study_queue:
            self.front_scroll_offset = 0
            self.back_scroll_offset = 0
            current_card_index = len(deck.cards) - len(study_queue)
            card = study_queue.popleft()

            if self.current_mode == "timed":
                elapsed = int(time.time() - self.study_start_time)
                if elapsed > 300:
                    self.display_message("Time's up! Study session complete.", pause=True)
                    break

            total_lines = self._show_card(card, current_card_index + 1, len(deck.cards), deck.name)
            show_back_mode = False
            
            while not show_back_mode:
                key = self.stdscr.getch()
                
                if key in [ord(' '), curses.KEY_ENTER, 10]:
                    show_back_mode = True
                elif key == curses.KEY_UP:
                    if self.front_scroll_offset > 0:
                        self.front_scroll_offset -= 1
                elif key == curses.KEY_DOWN:
                    rows, cols = self.stdscr.getmaxyx()
                    card_height = min(rows - 8, 18)
                    if self.front_scroll_offset < total_lines - (card_height - 2):
                        self.front_scroll_offset += 1
                
                self._show_card(card, current_card_index + 1, len(deck.cards), deck.name, show_back=show_back_mode)

            total_lines = self._show_card(
                card,
                current_card_index + 1,
                len(deck.cards),
                deck.name,
                show_back=True
            )

            rating_selected = False
            while not rating_selected:
                key = self.stdscr.getch()
                rating = {
                    ord('1'): 'got_it',
                    ord('2'): 'aw_man',
                    ord('3'): 'retry'
                }.get(key)

                if rating:
                    if rating == 'aw_man':
                        if random.choice([True, False]):
                            study_queue.insert(
                                random.randint(0, len(study_queue)),
                                card
                            )
                        else:
                            study_queue.append(card)
                    elif rating == 'retry':
                        study_queue.appendleft(card)

                    self._show_card(
                        card,
                        len(deck.cards) - len(study_queue),
                        len(deck.cards),
                        deck.name,
                        show_back=True,
                        rating=rating
                    )
                    rating_selected = True
                elif key == curses.KEY_UP:
                    if self.front_scroll_offset > 0:
                        self.front_scroll_offset -= 1
                elif key == curses.KEY_DOWN:
                    rows, cols = self.stdscr.getmaxyx()
                    card_height = min(rows - 8, 18)
                    if self.front_scroll_offset < total_lines - (card_height - 2):
                        self.front_scroll_offset += 1
                elif key in [ord('j'), ord('J')]:
                    rows, cols = self.stdscr.getmaxyx()
                    card_height = min(rows - 8, 18)
                    if self.back_scroll_offset < total_lines - (card_height - 2):
                        self.back_scroll_offset += 1
                elif key in [ord('k'), ord('K')]:
                    if self.back_scroll_offset > 0:
                        self.back_scroll_offset -= 1
                    
                self._show_card(
                    card,
                    len(deck.cards) - len(study_queue),
                    len(deck.cards),
                    deck.name,
                    show_back=True,
                    rating=rating
                )

        if self.current_mode == "timed":
            elapsed = int(time.time() - self.study_start_time)
            self.display_message(
                f"Session complete! Time: {elapsed//60}m {elapsed%60}s",
                pause=True
            )
        else:
            self.display_message("You have finished studying this deck!", pause=True)