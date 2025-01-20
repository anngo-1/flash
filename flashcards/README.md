# Flashcards Data Directory

This directory contains all deck and card data for the TUI Flashcards application.

## Structure

```
flashcards/
└── *.json              # Individual deck files
```

## Deck Files

Each deck is stored as a separate JSON file with the following format:

```json
{
    "name": "Deck Name",
    "cards": [
        {
            "front": "Card front text",
            "back": "Card back text"
        }
    ]
}
```

## Backup

To backup your flashcards, simply copy this entire directory. To restore, replace the directory with your backup copy.