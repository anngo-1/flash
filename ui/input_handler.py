import curses
import curses.ascii
import curses.textpad
import textwrap
from .base import BaseUI

class InputHandler(BaseUI):
    """Handles user input functionality."""
    def __init__(self, stdscr):
        super().__init__(stdscr)
        self._selected_index = 0
        self._top_index = 0
        self._edit_win = None  
        curses.curs_set(0)  # hide cursor by default

    def get_multiline_input(self, prompt, value=None):
        """Opens a text box for multiline input."""
        self.stdscr.erase()
        rows, cols = self.stdscr.getmaxyx()
        box_width = min(cols - 6, 70)
        box_height = min(rows - 8, 15)
        start_y = max(3, (rows - box_height) // 2)
        start_x = max(3, (cols - box_width) // 2)

        # draw prompt box
        prompt_lines = textwrap.wrap(prompt, box_width - 4)
        prompt_box_height = len(prompt_lines) + 2
        self._draw_box(
            start_y - prompt_box_height - 1,
            start_x,
            prompt_box_height,
            box_width,
            "Prompt",
            self.color_default
        )

        for i, line in enumerate(prompt_lines):
            self.stdscr.addstr(
                start_y - prompt_box_height + i + 1,
                start_x + (box_width - len(line)) // 2,
                line,
                curses.A_BOLD | self.color_default
            )

        # Draw input box
        self._draw_box(start_y, start_x, box_height, box_width, "Input", self.color_default)
        self._edit_win = curses.newwin(box_height - 2, box_width - 4, start_y + 1, start_x + 2)
        self._edit_win.bkgd(' ', self.color_default)

        if value:
            for i, line in enumerate(value.split('\n')):
                self._edit_win.addstr(i, 0, line[:box_width-4], self.color_default)

        instructions = "Press Enter to submit | CTRL+C to cancel | Arrow keys for new line"
        self.stdscr.addstr(
            start_y + box_height + 1,
            (cols - len(instructions)) // 2,
            instructions,
            curses.A_ITALIC | self.color_default
        )

        self.stdscr.refresh()
        text_box = curses.textpad.Textbox(self._edit_win, insert_mode=True)
        text_box.stripspaces = 0
        
        try:
            curses.curs_set(1)  
            contents = text_box.edit(self._validate_input)
        except KeyboardInterrupt:
            contents = None
        finally:
            curses.curs_set(0)  
            del self._edit_win
            self._edit_win = None
            self.stdscr.erase()

        return contents.rstrip() if contents and contents.strip() else None

    def _validate_input(self, ch):
        """Validate input in the textbox."""
        if ch == 27:  # ESC
            return 0
        elif ch == 10:  # Enter
            if self._edit_win:
                self._edit_win.nodelay(True)
                shift_check = self._edit_win.getch()
                self._edit_win.nodelay(False)
                return curses.ascii.BEL if shift_check == -1 else 10
            return 10
        return ch if ch in (
            curses.KEY_BACKSPACE,
            127,
            8,
            curses.KEY_LEFT,
            curses.KEY_RIGHT,
            curses.KEY_UP,
            curses.KEY_DOWN,
            curses.KEY_DC
        ) else ch

    def show_menu(self, title, options):
        """Display a menu and handle user selection.
        Now supports both navigation and direct key selection."""
        curses.curs_set(0)  # ensure cursor is hidden for menu
        self.stdscr.erase()
        rows, cols = self.stdscr.getmaxyx()
        max_visible_options = rows - 6
        menu_width = min(cols - 4, max(len(text) for _, text in options) + 12)
        
        if self._top_index > 0:
            self._selected_index = self._top_index = 0
            
        # create a mapping of option keys to their indices
        key_map = {key.lower(): i for i, (key, _) in enumerate(options)}
        
        while True:
            self.stdscr.erase()
            menu_height = min(len(options) + 4, max_visible_options + 4)
            menu_row = max(0, (rows - menu_height) // 2)
            menu_col = max(0, (cols - menu_width) // 2)
            
            self._draw_box(menu_row, menu_col, menu_height, menu_width, title)
            
            for i, (key, text) in enumerate(options):
                if self._top_index <= i < self._top_index + max_visible_options:
                    item_text = f" {key}. {text} "
                    item_col = menu_col + (menu_width - len(item_text)) // 2
                    
                    if i == self._selected_index:
                        self.stdscr.attron(self.color_highlight | curses.A_BOLD)
                        self.stdscr.addstr(menu_row + (i - self._top_index) + 2, item_col, item_text)
                        self.stdscr.attroff(self.color_highlight | curses.A_BOLD)
                    else:
                        self.stdscr.addstr(menu_row + (i - self._top_index) + 2, item_col, item_text)
            
            nav_help_text = "Navigate: j/k or ↑/↓, Select: Enter/letter key, Back: h"
            self.stdscr.addstr(
                rows - 2,
                max(0, (cols - len(nav_help_text)) // 2),
                nav_help_text,
                curses.A_ITALIC | self.color_default
            )
            
            self.stdscr.refresh()
            key = self.stdscr.getch()
            
            # check for direct key selection
            pressed_char = chr(key).lower() if 32 <= key <= 126 else None
            if pressed_char in key_map:
                self._selected_index = self._top_index = 0
                return options[key_map[pressed_char]][0]
            
            # handle other navigation keys
            if key in [ord('j'), curses.KEY_DOWN]:
                self._selected_index = min(self._selected_index + 1, len(options) - 1)
                if self._selected_index >= self._top_index + max_visible_options:
                    self._top_index = min(
                        self._selected_index - max_visible_options + 1,
                        len(options) - max_visible_options
                    )
            elif key in [ord('k'), curses.KEY_UP]:
                self._selected_index = max(self._selected_index - 1, 0)
                if self._selected_index < self._top_index:
                    self._top_index = max(0, self._selected_index)
            elif key in [curses.KEY_ENTER, 10, ord(' ')]:
                selected_option = options[self._selected_index][0]
                self._selected_index = self._top_index = 0
                return selected_option
            elif key == ord('h'):
                self._selected_index = self._top_index = 0
                return None
            elif key == 3:  # CTRL+C
                raise KeyboardInterrupt