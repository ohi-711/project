# space detective lawyer game
This title is subject to change. 

## Why I made this

I wanted to make a game so I talked to a friend and decided to make a game where you can play as a detective that travels across different planets. I've never made a game before so I'm hoping to learn some stuff from this project! 


## What it does

In this game, you play as a intergalactic space detective who collects clues and then eventually fight a boss. In the boss fight, there will be a battle mechanic that is similar to a trial (the one currently in place is temporary and will be improved upon later). The controls for walking are W, A, S, D, and the key for interacting with NPCs is E. 

## How it was made

This game was made using just Python and Python libraries. Specific libraries used were pygame, gif-pygame, and Pillow.

### Problems I ran into

- Getting GIFs to actually render as moving images instead of a single static frame was a problem that I ran into. This is because `pygame` doesn't support animated GIFs on its own, so frames have to be decoded manually with `Pillow` and played back through `gif-pygame`.

There are also still issues with the game/things I need to add:
- Collision with NPCs and inanimate objects looks weird because the obstacle size set is the size of the file. However, almost all of these assets are not cropped very well, and there is a lot of blank space.
- A lot of the assets are temporary replacements. The actual assets will be more polished and drawn later.
- A lot of the dialogue is also temmporary and will be improved upon later.
- Very few things have been added in terms of gameplay. More interesting things to do other than speak to NPCs will be added later.

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

I used AI was used to make a temporary/placeholder battle system (the courtroom trial cross-examination mechanic) that I may scrap completely or make changes to. This is because I haven't fully fleshed out how the gameplay should look like. AI was also used to help add in more trees because putting them all in myself is tiring.
