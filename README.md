# space detective lawyer game
(this title is subject to change) 

## Why I made this

I wanted to make a game, so I talked to a friend and decided to make a game where you can play as a detective who travels across different planets. I've never made a game before, so I'm hoping to learn some stuff from this project! 


## What it does

In this game, you play as an intergalactic space detective who collects clues and then eventually fights a boss. In the boss fight, there will be a battle mechanic that is similar to a trial (the one currently in place is temporary and will be improved upon later). The controls for walking are W, A, S, D, and the key for interacting with NPCs is E. 

## How it was made

This game was made using just Python and Python libraries. Specific libraries used were pygame, gif-pygame, and Pillow.

### Problems I ran into

- Getting GIFs to actually render as moving images instead of a single static frame was a problem that I ran into. This is because `pygame` doesn't support animated GIFs on its own, so frames have to be decoded manually with `Pillow` and played back through `gif-pygame`.
- Ran into some issues with making an .exe but they were resolved pretty fast as well.
- It was also somewhat difficult adding the chasing sequence on the second planet. This is because when the player switches rooms, there has to be a delay depending on how far the figure was from the player.

There are also still issues with the game/things I need to add:
- Collision with NPCs and inanimate objects looks weird because the obstacle size set is the size of the file. However, almost all of these assets are not cropped very well, and there is a lot of blank space.
- A lot of the assets are temporary replacements. The actual assets will be more polished and drawn later.
- A lot of the dialogue is also temporary and will be improved upon later.
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
<img width="630" height="500" alt="thumbnail" src="https://github.com/user-attachments/assets/88c5fcda-9f70-48ba-afe6-fec94e29c3f1" />
<img width="1596" height="893" alt="image" src="https://github.com/user-attachments/assets/d344e980-1eb0-42cb-be47-4ff0dc513f12" />
<img width="1592" height="882" alt="image" src="https://github.com/user-attachments/assets/145e8904-7b3b-4cfe-b23c-be3598f22d2f" />


## AI disclosure

I used AI was used to make a temporary/placeholder battle system (the courtroom trial cross-examination mechanic) that I may scrap completely or make changes to. This is because I haven't fully fleshed out how the gameplay should look like. AI was also used to help fix the issues I encountered when trying to make an .exe file. AI was also used to help add in more trees because putting them all in myself is tiring.
