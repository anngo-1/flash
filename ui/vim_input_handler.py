import curses
import curses.ascii
import textwrap
from .base import BaseUI

class VimInputHandler(BaseUI):
    """Handles user input functionality with Vim-like multiline input and scrolling."""
    def __init__(self, stdscr):
        super().__init__(stdscr)
        self._selected_index = 0
        self._top_index = 0
        self._edit_win = None
        self._cursor_y = 0
        self._cursor_x = 0
        self._scroll_offset = 0  # track scroll position
        self._text_lines = [""]
        self._insert_mode = False
        self._paste_buffer = []  # internal paste buffer
        self._visual_mode = False
        self._visual_start = (0, 0)  # (y, x)
        curses.curs_set(0)  # hide cursor by default

    def get_multiline_input(self, prompt, value=None, language=None):
        """Opens a Vim-like text box for multiline input."""
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

        # Initialize text
        self._text_lines = value.splitlines() if value else [""]
        self._cursor_y = 0
        self._cursor_x = 0
        self._scroll_offset = 0
        self._insert_mode = False
        self._visual_mode = False
        self._paste_buffer = []

        # Draw input box
        self._draw_box(start_y, start_x, box_height, box_width, "Input", self.color_default)
        self._edit_win = curses.newwin(box_height - 2, box_width - 4, start_y + 1, start_x + 2)
        self._edit_win.bkgd(' ', self.color_default)
        self._edit_win.keypad(True)

        instructions = "Vim-like editing | :wq to save | :q! to cancel | :paste to paste"
        self.stdscr.addstr(
            start_y + box_height + 1,
            (cols - len(instructions)) // 2,
            instructions,
            curses.A_ITALIC | self.color_default
        )

        self.stdscr.refresh()

        try:
            curses.curs_set(1)
            result = self._vim_like_input_loop(box_height - 2, box_width - 4)
        except KeyboardInterrupt:
            result = None
        finally:
            curses.curs_set(0)
            del self._edit_win
            self._edit_win = None
            self.stdscr.erase()

        return "\n".join(result) if result is not None else None
    def _vim_like_input_loop(self, height, width):
        """Handles the main loop for the Vim-like input with scrolling support."""
        command_buffer = []  # buffer to store multi-key commands
        
        while True:
            self._adjust_scroll(height)
            self._draw_vim_editor(height, width)
            key = self._edit_win.getch()

            if key == curses.KEY_RESIZE:
                continue

            if self._insert_mode:
                if key == curses.ascii.ESC:
                    self._insert_mode = False
                    self._cursor_x = max(0, self._cursor_x - 1)
                else:
                    self._handle_insert_mode(key)
            else:  # normal mode
                if command_buffer:
                    command = command_buffer[0]
                    if command == ord('d'):
                        if key == ord('d'):  # dd - delete line
                            if len(self._text_lines) > 1:
                                self._paste_buffer = [self._text_lines.pop(self._cursor_y)]
                                self._cursor_x = 0
                                if self._cursor_y >= len(self._text_lines):
                                    self._cursor_y = len(self._text_lines) - 1
                            else:
                                self._text_lines[0] = ""
                        elif key == ord('w'):  # dw - delete word
                            self._delete_word()
                        elif key == ord('e'):  # de - delete to end of word
                            self._delete_to_word_end()
                        elif key == ord('$'):  # d$ - delete to end of line
                            self._delete_to_line_end()
                        elif key == ord('0'):  # d0 - delete to start of line
                            self._delete_to_line_start()
                        elif key == ord('b'):  # db - delete backward word
                            self._delete_word_backward()
                        command_buffer.clear()
                        continue

                if key == ord('d'):
                    command_buffer = [key]
                elif key == ord(':'):
                    command = self._get_command()
                    if command == "wq":
                        return self._text_lines
                    elif command == "q!":
                        return None
                    elif command == "paste":
                        paste_result = self._handle_paste()
                        if paste_result is not None:
                            self._insert_text_at_cursor(paste_result)
                else:
                    self._handle_normal_mode(key)

            self._adjust_cursor_within_bounds(height, width)

    def _handle_normal_mode(self, key):
        """Handle keys in normal mode."""
        if key == ord('h'):
            self._cursor_x = max(0, self._cursor_x - 1)
        elif key == ord('j'):
            if self._cursor_y < len(self._text_lines) - 1:
                self._cursor_y += 1
        elif key == ord('k'):
            if self._cursor_y > 0:
                self._cursor_y -= 1
        elif key == ord('l'):
            self._cursor_x = min(len(self._text_lines[self._cursor_y]), self._cursor_x + 1)
        elif key == ord('i'):
            self._insert_mode = True
        elif key == ord('a'):
            self._cursor_x = min(len(self._text_lines[self._cursor_y]), self._cursor_x + 1)
            self._insert_mode = True
        elif key == ord('A'):
            self._cursor_x = len(self._text_lines[self._cursor_y])
            self._insert_mode = True
        elif key == ord('o'):
            self._text_lines.insert(self._cursor_y + 1, "")
            self._cursor_y += 1
            self._cursor_x = 0
            self._insert_mode = True
        elif key == ord('O'):
            self._text_lines.insert(self._cursor_y, "")
            self._cursor_x = 0
            self._insert_mode = True
        elif key == ord('v'):
            self._visual_mode = True
            self._visual_start = (self._cursor_y, self._cursor_x)
        elif key == ord('y'):
            if self._visual_mode:
                self._copy_visual_selection()
                self._visual_mode = False
        elif key == ord('p'):
            self._paste_text(after=True)
        elif key == ord('P'):
            self._paste_text(after=False)
        elif key == ord('G'):
            self._cursor_y = len(self._text_lines) - 1
        elif key == ord('g'):
            next_key = self._edit_win.getch()
            if next_key == ord('g'):
                self._cursor_y = 0
        return None  
    def _draw_vim_editor(self, height, width):
        """Draws the current state of the Vim-like editor with scrolling support."""
        self._edit_win.erase()
        visible_range = range(self._scroll_offset, min(len(self._text_lines), self._scroll_offset + height - 1))
        
        for i, line_idx in enumerate(visible_range):
            line = self._text_lines[line_idx]
            if self._visual_mode:
                self._highlight_visual_selection(line_idx, line, width, i)
            else:
                self._edit_win.addstr(i, 0, line[:width], self.color_default)

        if self._scroll_offset > 0:
            self._edit_win.addstr(0, width - 1, "↑", curses.A_DIM | self.color_default)
        if self._scroll_offset + height - 1 < len(self._text_lines):
            self._edit_win.addstr(height - 2, width - 1, "↓", curses.A_DIM | self.color_default)

        # mode indicator in the bottom right
        if self._insert_mode:
            mode_indicator = "INSERT"
            mode_attr = curses.A_BOLD | self.color_highlight
        elif self._visual_mode:
            mode_indicator = "VISUAL"
            mode_attr = curses.A_BOLD | self.color_highlight
        else:
            mode_indicator = "NORMAL"
            mode_attr = curses.A_DIM | self.color_default
        
        mode_x = width - len(mode_indicator) - 1
        if mode_x >= 0:  # Only draw if there's space
            self._edit_win.addstr(height - 1, mode_x, mode_indicator, mode_attr)

        cursor_y = self._cursor_y - self._scroll_offset
        try:
            if 0 <= cursor_y < height - 1:
                self._edit_win.move(cursor_y, self._cursor_x)
        except curses.error:
            pass
        self._edit_win.refresh()

    def _handle_insert_mode(self, key):
        """Handle keys in insert mode."""
        if key == curses.KEY_ENTER or key == 10:
            self._text_lines[self._cursor_y] = self._text_lines[self._cursor_y][:self._cursor_x]
            self._text_lines.insert(self._cursor_y + 1, self._text_lines[self._cursor_y][self._cursor_x:])
            self._cursor_y += 1
            self._cursor_x = 0
        elif key == curses.KEY_BACKSPACE or key == 127:
            if self._cursor_x > 0:
                self._text_lines[self._cursor_y] = (
                    self._text_lines[self._cursor_y][:self._cursor_x - 1] +
                    self._text_lines[self._cursor_y][self._cursor_x:]
                )
                self._cursor_x -= 1
            elif self._cursor_y > 0:
                prev_line_len = len(self._text_lines[self._cursor_y - 1])
                self._text_lines[self._cursor_y - 1] += self._text_lines[self._cursor_y]
                del self._text_lines[self._cursor_y]
                self._cursor_y -= 1
                self._cursor_x = prev_line_len
        elif key == curses.KEY_DC:  # Delete
            if self._cursor_x < len(self._text_lines[self._cursor_y]):
                self._text_lines[self._cursor_y] = (
                    self._text_lines[self._cursor_y][:self._cursor_x] +
                    self._text_lines[self._cursor_y][self._cursor_x + 1:]
                )
            elif self._cursor_y < len(self._text_lines) - 1:
                self._text_lines[self._cursor_y] += self._text_lines[self._cursor_y + 1]
                del self._text_lines[self._cursor_y + 1]
        elif 32 <= key <= 126:  
            char = chr(key)
            self._text_lines[self._cursor_y] = (
                self._text_lines[self._cursor_y][:self._cursor_x] +
                char +
                self._text_lines[self._cursor_y][self._cursor_x:]
            )
            self._cursor_x += 1

    def _handle_normal_mode(self, key):
        """Handle keys in normal mode."""
        if key == ord(':'):
            command = self._get_command()
            if command == "wq":
                return self._text_lines
            elif command == "q!":
                return None
            elif command == "paste":
                paste_result = self._handle_paste()
                if paste_result is not None:
                    self._insert_text_at_cursor(paste_result)
        elif key == ord('h'):
            self._cursor_x = max(0, self._cursor_x - 1)
        elif key == ord('j'):
            if self._cursor_y < len(self._text_lines) - 1:
                self._cursor_y += 1
        elif key == ord('k'):
            if self._cursor_y > 0:
                self._cursor_y -= 1
        elif key == ord('l'):
            self._cursor_x = min(len(self._text_lines[self._cursor_y]), self._cursor_x + 1)
        elif key == ord('i'):
            self._insert_mode = True
        elif key == ord('a'):
            self._cursor_x = min(len(self._text_lines[self._cursor_y]), self._cursor_x + 1)
            self._insert_mode = True
        elif key == ord('A'):
            self._cursor_x = len(self._text_lines[self._cursor_y])
            self._insert_mode = True
        elif key == ord('o'):
            self._text_lines.insert(self._cursor_y + 1, "")
            self._cursor_y += 1
            self._cursor_x = 0
            self._insert_mode = True
        elif key == ord('O'):
            self._text_lines.insert(self._cursor_y, "")
            self._cursor_x = 0
            self._insert_mode = True
        elif key == ord('v'):
            self._visual_mode = True
            self._visual_start = (self._cursor_y, self._cursor_x)
        elif key == ord('y'):
            if self._visual_mode:
                self._copy_visual_selection()
                self._visual_mode = False
        elif key == ord('p'):
            self._paste_text(after=True)
        elif key == ord('P'):
            self._paste_text(after=False)
        elif key == ord('G'):
            self._cursor_y = len(self._text_lines) - 1
        elif key == ord('g'):
            next_key = self._edit_win.getch()
            if next_key == ord('g'):
                self._cursor_y = 0

    def _delete_word(self):
        """Delete from cursor to start of next word."""
        line = self._text_lines[self._cursor_y]
        if self._cursor_x >= len(line):
            if self._cursor_y < len(self._text_lines) - 1:
                self._paste_buffer = [line[self._cursor_x:] + self._text_lines[self._cursor_y + 1][:1]]
                self._text_lines[self._cursor_y] = line[:self._cursor_x]
                self._text_lines[self._cursor_y + 1] = self._text_lines[self._cursor_y + 1][1:]
            return

        pos = self._cursor_x
        while pos < len(line) and line[pos].isspace():
            pos += 1
        while pos < len(line) and not line[pos].isspace():
            pos += 1
        
        self._paste_buffer = [line[self._cursor_x:pos]]
        self._text_lines[self._cursor_y] = line[:self._cursor_x] + line[pos:]

    def _delete_to_word_end(self):
        """Delete from cursor to end of current word."""
        line = self._text_lines[self._cursor_y]
        if self._cursor_x >= len(line):
            return

        pos = self._cursor_x
        if not line[pos].isspace():
            while pos < len(line) and not line[pos].isspace():
                pos += 1
        else:
            while pos < len(line) and line[pos].isspace():
                pos += 1
            while pos < len(line) and not line[pos].isspace():
                pos += 1

        self._paste_buffer = [line[self._cursor_x:pos]]
        self._text_lines[self._cursor_y] = line[:self._cursor_x] + line[pos:]


    def _delete_word_backward(self):
        """Delete word before cursor."""
        line = self._text_lines[self._cursor_y]
        if self._cursor_x == 0:
            if self._cursor_y > 0:
                prev_line = self._text_lines[self._cursor_y - 1]
                self._paste_buffer = [prev_line[-1:] + line[:1]]
                self._text_lines[self._cursor_y - 1] = prev_line[:-1]
                self._text_lines[self._cursor_y] = line[1:]
            return

        pos = self._cursor_x - 1
        while pos > 0 and line[pos-1].isspace():
            pos -= 1
        while pos > 0 and not line[pos-1].isspace():
            pos -= 1

        self._paste_buffer = [line[pos:self._cursor_x]]
        self._text_lines[self._cursor_y] = line[:pos] + line[self._cursor_x:]
        self._cursor_x = pos

    def _delete_to_line_end(self):
        """Delete from cursor to end of line."""
        line = self._text_lines[self._cursor_y]
        if self._cursor_x < len(line):
            self._paste_buffer = [line[self._cursor_x:]]
            self._text_lines[self._cursor_y] = line[:self._cursor_x]

    def _delete_to_line_start(self):
        """Delete from cursor to start of line."""
        line = self._text_lines[self._cursor_y]
        if self._cursor_x > 0:
            self._paste_buffer = [line[:self._cursor_x]]
            self._text_lines[self._cursor_y] = line[self._cursor_x:]
            self._cursor_x = 0

    def _highlight_visual_selection(self, line_idx, line, width, display_idx):
        """Highlights the visually selected text with scroll offset support."""
        start_y, start_x = min(self._visual_start, (self._cursor_y, self._cursor_x))
        end_y, end_x = max(self._visual_start, (self._cursor_y, self._cursor_x))

        if start_y <= line_idx <= end_y:
            row_text = line[:width]
            if line_idx == start_y == end_y:
                self._edit_win.addstr(display_idx, 0, row_text[:start_x], self.color_default)
                self._edit_win.addstr(display_idx, start_x, row_text[start_x:end_x + 1], self.color_highlight)
                self._edit_win.addstr(display_idx, end_x + 1, row_text[end_x + 1:], self.color_default)
            elif line_idx == start_y:
                self._edit_win.addstr(display_idx, 0, row_text[:start_x], self.color_default)
                self._edit_win.addstr(display_idx, start_x, row_text[start_x:], self.color_highlight)
            elif line_idx == end_y:
                self._edit_win.addstr(display_idx, 0, row_text[:end_x + 1], self.color_highlight)
                self._edit_win.addstr(display_idx, end_x + 1, row_text[end_x + 1:], self.color_default)
            else:
                self._edit_win.addstr(display_idx, 0, row_text, self.color_highlight)
        else:
            self._edit_win.addstr(display_idx, 0, line[:width], self.color_default)

    def _copy_visual_selection(self):
        """Copies the currently visually selected text to the paste buffer."""
        if not self._visual_mode:
            return

        start_coords = min(self._visual_start, (self._cursor_y, self._cursor_x))
        end_coords = max(self._visual_start, (self._cursor_y, self._cursor_x))
        start_y, start_x = start_coords
        end_y, end_x = end_coords

        self._paste_buffer = []
        for y in range(start_y, end_y + 1):
            line = self._text_lines[y]
            if y == start_y and y == end_y:
                self._paste_buffer.append(line[start_x:end_x + 1])
            elif y == start_y:
                self._paste_buffer.append(line[start_x:])
            elif y == end_y:
                self._paste_buffer.append(line[:end_x + 1])
            else:
                self._paste_buffer.append(line)

    def _paste_text(self, after):
        """Pastes the content of the internal paste buffer."""
        if not self._paste_buffer:
            return

        if after:
            target_y = self._cursor_y
            target_x = self._cursor_x + 1 if self._cursor_x < len(self._text_lines[self._cursor_y]) else self._cursor_x
        else:
            target_y = self._cursor_y
            target_x = self._cursor_x

        if len(self._paste_buffer) > 1:
            remainder = self._text_lines[target_y][target_x:]
            self._text_lines[target_y] = self._text_lines[target_y][:target_x] + self._paste_buffer[0]
            
            self._text_lines[target_y + 1:target_y + 1] = self._paste_buffer[1:]
            last_line_idx = target_y + len(self._paste_buffer)
            self._text_lines[last_line_idx - 1] += remainder
            
            self._cursor_y = last_line_idx - 1
            self._cursor_x = len(self._text_lines[self._cursor_y]) - len(remainder)
        else:
            line = self._paste_buffer[0]
            self._text_lines[target_y] = (
                self._text_lines[target_y][:target_x] +
                line +
                self._text_lines[target_y][target_x:]
            )
            self._cursor_x = target_x + len(line)

    def _handle_paste(self):
        """Attempts to get clipboard content."""
        curses.endwin()  # End curses temporarily
        try:
            import subprocess
            paste_content = subprocess.check_output(['xclip', '-selection', 'clipboard', '-o'], text=True)
            return paste_content.splitlines()
        except (FileNotFoundError, subprocess.CalledProcessError):
            return None
        finally:
            self.stdscr = curses.initscr()  # Re-initialize curses
            curses.noecho()
            curses.cbreak()
            self.stdscr.keypad(True)
            self._edit_win.keypad(True)

    def _get_command(self):
        """Get command input from the user."""
        rows, _ = self._edit_win.getmaxyx()
        command_line = ":"
        self._edit_win.addstr(rows - 1, 0, command_line, curses.A_REVERSE)
        curses.curs_set(1)
        curses.echo()
        self._edit_win.refresh()
        command = self._edit_win.getstr(rows - 1, 1).decode('utf-8')
        curses.noecho()
        curses.curs_set(0)
        return command.strip()

    def _adjust_cursor_within_bounds(self, height, width):
        """Keeps the cursor within the text boundaries."""
        self._cursor_y = max(0, min(len(self._text_lines) - 1, self._cursor_y))
        self._cursor_x = max(0, min(len(self._text_lines[self._cursor_y]), self._cursor_x))
        self._adjust_scroll(height)

    def _adjust_scroll(self, height):
        """Adjusts scroll position to keep cursor in view."""
        if self._cursor_y < self._scroll_offset:
            self._scroll_offset = self._cursor_y
        elif self._cursor_y >= self._scroll_offset + height - 1:
            self._scroll_offset = self._cursor_y - height + 2

        max_scroll = max(0, len(self._text_lines) - height + 1)
        self._scroll_offset = max(0, min(self._scroll_offset, max_scroll))

    def show_menu(self, title, options):
        """Display a menu and handle user selection."""
        curses.curs_set(0)  # hide cursor for menu
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

            nav_help_text = "Navigate: j/k or ↑/↓, Select: Enter/Number"
            self.stdscr.addstr(
                rows - 2,
                max(0, (cols - len(nav_help_text)) // 2),
                nav_help_text,
                curses.A_ITALIC | self.color_default
            )

            self.stdscr.refresh()

            try:
                key = self.stdscr.getch()
            except KeyboardInterrupt:
                return None

            if key == 3:  # Ctrl+C
                return None

            pressed_char = chr(key).lower() if 32 <= key <= 126 else None
            if pressed_char in key_map:
                self._selected_index = self._top_index = 0
                return options[key_map[pressed_char]][0]

            if key in [curses.KEY_DOWN, ord('j')]:  # down arrow or j
                self._selected_index = min(self._selected_index + 1, len(options) - 1)
                if self._selected_index >= self._top_index + max_visible_options:
                    self._top_index = min(
                        self._selected_index - max_visible_options + 1,
                        len(options) - max_visible_options
                    )
            elif key in [curses.KEY_UP, ord('k')]:  # up arrow or k
                self._selected_index = max(self._selected_index - 1, 0)
                if self._selected_index < self._top_index:
                    self._top_index = max(0, self._selected_index)
            elif key in [curses.KEY_ENTER, 10, ord(' '), ord('l')]:  # enter, space, or l
                selected_option = options[self._selected_index][0]
                self._selected_index = self._top_index = 0
                return selected_option
            elif key == ord('h'):  # h to go back
                return None
            elif key == ord('G'):  # G to go to bottom
                self._selected_index = len(options) - 1
                if len(options) > max_visible_options:
                    self._top_index = len(options) - max_visible_options
            elif key == ord('g'):  # gg to go to top
                next_key = self.stdscr.getch()
                if next_key == ord('g'):
                    self._selected_index = 0
                    self._top_index = 0
            elif key == 3:  # CTRL+C
                raise KeyboardInterrupt