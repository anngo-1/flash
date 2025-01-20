# flash

**flash** is a flashcard application in the terminal built with Python and curses.
(flash is running below on ghostty, but also works on most common terminals)
<br>
<br>
![image](https://github.com/user-attachments/assets/38298146-7bba-464b-85a8-ae8efce5d7b3)
Starting screen of flash.
<br>
<br>
![image](https://github.com/user-attachments/assets/1be176cd-cff5-424f-a386-4e7b4b51eb74)
Card deck creation.

![image](https://github.com/user-attachments/assets/70240fb2-6e81-4117-806d-90c7790fe7a4)
Deck options.

## Features

- Create and manage multiple decks of flashcards
- Queue system for card review:
  - Cards you miss are automatically requeued
  - Randomized requeuing for spaced repetition
  - Queue manipulation based on performance
- Study modes:
  - Study your cards in order
  - Study your cards shuffled
  - Timed challenge mode (5 minutes)
- Keyboard navigation 



## Study Interface

- Shows current progress through deck
- Displays timer in timed mode
- Color-coded feedback for correct/incorrect responses
- Dynamic queue management:
  - "Got it!" - Card removed from queue
  - "Retry" - Card moved to front of queue
  - "Aw man..." - Card randomly reinserted into queue

[Screenshot placeholder: Study interface]

## Project Structure

```
tui-flashcards/
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
    └── main.py           # Main application loop and menu system
```

## Installation

```bash
# Clone the repository
git clone https://github.com/anngo-1/flash.git
cd flash

# Run the application
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

[Screenshot placeholder: Card creation interface]

## Data Storage

Cards are stored as JSON files in a `flashcards` directory, making them easy to backup or share.
