# idk what to call the game yet


## Why I made this



## What it does

## Tech stack

This game was made using just Python and Python libraries. It will be hosted using itch.io probably. Specific libraries used were pygame, gif-pygame, and Pillow.

## How it was made


### Problems I ran into

- Getting GIFs to actually render as moving images instead of a single static frame was a problem that I ran into. This is because `pygame` doesn't support animated GIFs on its own, so frames have to be decoded manually with `Pillow` and played back through `gif-pygame`.

## Development

1. Clone the source code to your device
   ```sh
   git clone https://github.com/ohi-711/project.git
   ```
2. Install the dependencies
   ```sh
   pip install pygame
   pip install gif-pygame
   pip install Pillow
   ```
3. Run the game
   ```sh
   python main.py
   ```

## Demo


## AI disclosure

I used AI was used to make a temporary/placeholder battle system (the courtroom trial cross-examination mechanic) that I may scrap completely or make changes to. This is because I haven't fully fleshed out how the gameplay should look like.
