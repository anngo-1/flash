import curses
from ui.main import TUI

def main():
    """Main function to initialize and run the TUI."""
    try:
        stdscr = curses.initscr()
        curses.noecho()  
        curses.cbreak() 
        stdscr.keypad(True) 
        app = TUI(stdscr)
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