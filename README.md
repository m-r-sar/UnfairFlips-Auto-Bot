# Unfair Flips Auto-Bot

An automation script written in Python for the game **Unfair Flips**. 
This bot reads game memory using `pymem` to track money and automatically purchases upgrades based on an optimized strategy using `pyautogui`.

## Features
-  **Memory Reading:** Directly reads money values from RAM for instant reaction.
-  **Auto-Clicking:** Automatically flips the coin.
-  **Smart Upgrades:** Prioritizes upgrades logic (Speed > Chance > Combo > Worth).
-  **Save System:** Remembers your upgrade levels in `upgrades.json` so you don't lose progress if you restart the bot.

## How to Use
1. Install dependencies (requirements.txt)
2. Open the game
3. Important: The bot uses hardcoded screen coordinates. You must ensure the game window is in the default position or update the coordinates in main.py (variables flip_button_cords, etc.)
4. Run the script
5. Press ENTER to start the bot
6. Press H to exit

### Disclaimer
This software is for educational purposes only. Use it at your own risk.
