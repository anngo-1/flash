# flash

**flash** is a flashcard application in the terminal built with Python and curses.
(flash is running below on ghostty, but also works on most common terminals)
<br>
<br>
Starting screen of flash.
![image](https://github.com/user-attachments/assets/07d4c50e-75ca-463b-bc41-ac04a8f39fe6)

Card deck creation with vim-like editor.
![image](https://github.com/user-attachments/assets/4b6bcade-fc08-4477-8a8f-0a05ced7c9b9)

Deck options.
![image](https://github.com/user-attachments/assets/83338844-b8e3-434a-af7f-25c02f3ce6fe)

Timed test with a flashcard deck
![image](https://github.com/user-attachments/assets/18b7a038-0692-4c72-a536-4a854326c405)

![image](https://github.com/user-attachments/assets/fd14f257-5949-4047-8249-68f496c92943)


## Features

- Create and manage multiple decks of flashcards
- Limited vim keybinding support for text editing
- Queue system for card review:
  - Cards you miss are automatically requeued
  - Randomized requeuing for spaced repetition
  - Queue manipulation based on performance
- Study modes:
  - Study your cards in order
  - Study your cards shuffled
  - Timed challenge mode (5 minutes)
- Keyboard navigation 

## Supported Vim Keybindings

### Navigation

| Key | Mode | Description |
|-----|------|-------------|
| `h` | Normal | Move cursor left |
| `j` | Normal | Move cursor down |
| `k` | Normal | Move cursor up |
| `l` | Normal | Move cursor right |
| `G` | Normal | Go to last line |
| `gg` | Normal | Go to first line |

### Editing

| Key | Mode | Description |
|-----|------|-------------|
| `i` | Normal | Enter insert mode at cursor |
| `a` | Normal | Enter insert mode after cursor |
| `A` | Normal | Enter insert mode at end of line |
| `o` | Normal | Open new line below and enter insert mode |
| `O` | Normal | Open new line above and enter insert mode |
| `ESC` | Insert | Exit insert mode |

### Deletion Commands

| Key | Mode | Description |
|-----|------|-------------|
| `x` | Normal | Delete at current cursor |
| `dd` | Normal | Delete current line |
| `dw` | Normal | Delete from cursor to start of next word |
| `de` | Normal | Delete from cursor to end of current word |
| `d$` | Normal | Delete from cursor to end of line |
| `d0` | Normal | Delete from cursor to start of line |
| `db` | Normal | Delete word before cursor |

### Visual Mode

| Key | Mode | Description |
|-----|------|-------------|
| `v` | Normal | Enter visual mode |
| `y` | Visual | Yank (copy) selected text |
| `ESC` | Visual | Exit visual mode |

### Clipboard Operations

| Key | Mode | Description |
|-----|------|-------------|
| `p` | Normal | Paste after cursor |
| `P` | Normal | Paste before cursor |
| `:paste` | Command | Paste from system clipboard |

### File Operations

| Key | Mode | Description |
|-----|------|-------------|
| `:wq` | Command | Save and quit |
| `:q!` | Command | Quit without saving |

### Special Keys

| Key | Mode | Description |
|-----|------|-------------|
| `Enter` | Insert | Create new line |
| `Backspace` | Insert | Delete character before cursor |

## Study Interface

- Shows current progress through deck
- Displays timer in timed mode
- Color-coded feedback for correct/incorrect responses
- Dynamic queue management:
  - "Got it!" - Card removed from queue
  - "Retry" - Card moved to front of queue
  - "Aw man..." - Card randomly reinserted into queue


## Project Structure

```
flash/
├── flashcards.py          # Main entry point, initializes curses and TUI
├── flashcards/           # Data directory for deck storage
├── models/
│   ├── card.py           # Card class for flashcard data
│   ├── deck.py           # Deck class with queue and card management
│   └── deck_manager.py   # Handles saving/loading decks as JSON
└── ui/
    ├── base.py           # Common UI utilities and color management
    ├── card_display.py   # Study interface and queue logic
    ├── deck_actions.py   # Deck creation, editing, deletion
    ├── input_handler.py  # Keyboard input and text entry processing
    ├── vim_input_handler.py  # Vim keybindings input and text entry processing
    └── main.py           # Main application loop and menu system
```

## Installation

```bash
# Clone the repository
git clone https://github.com/anngo-1/flash.git
cd flash
```
If you are on Windows, you must install the windows curses python package with:

```bash
# Skip this step if on Mac/Linux!
pip install windows-curses
```

Then, you can either run flash in vim mode or no vim mode. In Vim mode, you use vim keybinds in your text editor for creating flashcards and decks. In no vim mode, you use a basic editor without vim keybindings.

```bash
# Option 1: Run the application in no vim mode
python flashcards.py --novim
```

```bash
# Option 2:Run the application in vim mode
python flashcards.py
```
Requirements:
- Python 3.x
- No external dependencies

## Usage

Navigate using:
- Arrow keys / hjkl for movement
- Enter/Space to select
- Numbers for quick selection
- Ctrl+C to exit


## Data Storage

Cards are stored as JSON files in a `flashcards` directory, making them easy to backup or share.
