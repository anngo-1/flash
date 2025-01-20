import curses
import textwrap

class BaseUI:
    """Base class for UI components with common functionality."""
    def __init__(self, stdscr):
        """Initialize the base UI with standard screen object."""
        self.stdscr = stdscr
        self._init_colors()

    def _init_colors(self):
        """Initialize color pairs for the UI."""
        curses.start_color()
        curses.use_default_colors()
        for pair_num, fg in [
            (1, curses.COLOR_WHITE), 
            (2, curses.COLOR_WHITE),
            (3, curses.COLOR_GREEN), 
            (4, curses.COLOR_RED), 
            (5, curses.COLOR_BLUE)
        ]:
            curses.init_pair(pair_num, fg, -1)
        self.color_default = curses.color_pair(1)
        self.color_highlight = curses.color_pair(2) | curses.A_REVERSE
        self.color_correct = curses.color_pair(3)
        self.color_incorrect = curses.color_pair(4)
        self.color_progress = curses.color_pair(5)

    def _draw_box(self, r, c, h, w, title="", border_color=None):
        """Draw a box with an optional title."""
        rows, cols = self.stdscr.getmaxyx()
        border_color = border_color or self.color_default
        
        if not all([0 <= r < rows, 0 <= c < cols, r + h <= rows, c + w <= cols]):
            return

        self.stdscr.attron(border_color)
        
        # draw corners
        corners = [
            (r, c, curses.ACS_ULCORNER),
            (r, min(c + w - 1, cols - 1), curses.ACS_URCORNER),
            (min(r + h - 1, rows - 1), c, curses.ACS_LLCORNER),
            (min(r + h - 1, rows - 1), min(c + w - 1, cols - 1), curses.ACS_LRCORNER)
        ]
        for pos_r, pos_c, ch in corners:
            if 0 <= pos_r < rows and 0 <= pos_c < cols:
                self.stdscr.addch(pos_r, pos_c, ch)

        # draw horizontal lines
        if c + 1 < cols and c + w - 1 > 0:
            self.stdscr.hline(r, c + 1, curses.ACS_HLINE, min(w - 2, cols - c - 1))
            self.stdscr.hline(r + h - 1, c + 1, curses.ACS_HLINE, min(w - 2, cols - c - 1))

        # draw vertical lines
        if r + 1 < rows and r + h - 1 > 0:
            self.stdscr.vline(r + 1, c, curses.ACS_VLINE, min(h - 2, rows - r - 1))
            self.stdscr.vline(r + 1, c + w - 1, curses.ACS_VLINE, min(h - 2, rows - r - 1))

        # draw title if provided
        if title:
            title_text = f" {title} "
            title_start_col = max(0, c + (w - len(title_text)) // 2)
            if title_start_col < cols:
                self.stdscr.addstr(r, title_start_col, title_text, curses.A_BOLD)

        self.stdscr.attroff(border_color)

    def display_message(self, msg, row=None, pause=False):
        """Display a message on the screen."""
        self.stdscr.erase()
        rows, cols = self.stdscr.getmaxyx()
        msg_lines = textwrap.wrap(msg, cols - 4)
        start_row = (rows - len(msg_lines)) // 2 if row is None else row
        
        for i, line in enumerate(msg_lines):
            self.stdscr.addstr(
                start_row + i,
                max(0, (cols - len(line)) // 2),
                line,
                curses.A_BOLD | self.color_default
            )

        if pause:
            prompt = "Press any key to continue..."
            prompt_row = rows - 2 
            prompt_col = max(0, (cols - len(prompt)) // 2)  
            self.stdscr.addstr(
                prompt_row,
                prompt_col,
                prompt,
                self.color_default
            )

        self.stdscr.refresh()
        
        if pause:
            while self.stdscr.getch() not in [ord(' '), curses.KEY_ENTER, 10]:
                pass