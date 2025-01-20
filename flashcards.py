import curses
import argparse
from ui.main import TUI
from ui.input_handler import SimpleInputHandler
from ui.vim_input_handler import VimInputHandler

def parse_args():
    parser = argparse.ArgumentParser(description="Flashcard Application")
    parser.add_argument('--novim', action='store_true', help='Use Vim-style input mode')
    return parser.parse_args()

def main():
    """Main function to initialize and run the TUI."""
    args = parse_args()
    
    try:
        stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(True)

        InputHandlerClass = SimpleInputHandler if args.novim else VimInputHandler
        input_handler = InputHandlerClass(stdscr)

        app = TUI(stdscr, input_handler)
        app.run()

    except KeyboardInterrupt:
        pass
    finally:
        if 'stdscr' in locals():
            stdscr.keypad(False)
            curses.nocbreak()
            curses.echo()
            curses.endwin()

if __name__ == "__main__":
    main()