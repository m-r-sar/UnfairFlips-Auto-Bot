from pymem import Pymem
from pymem.process import module_from_name
import time
import pyautogui as gui
from pynput import keyboard
import threading
import json
import os

bot_running = False


def get_pointer_addr(pm, base_addr, offsets):
    try:
        addr = pm.read_longlong(base_addr)
        for offset in offsets[:-1]:
            addr = pm.read_longlong(addr + offset)
        return addr + offsets[-1]
    except Exception as e:
        # Avoid spamming errors in the console, only print critical ones
        return None


def load_upgrades(filename):
    default_upgrades = {"chance": 0, "speed": 0, "combo": 0, "worth": 0}
    try:
        with open(filename, "r") as f:
            print("Loading upgrades...")
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("Upgrades file not found or corrupted. Creating new one.")
        with open(filename, "w") as f:
            json.dump(default_upgrades, f, indent=4)
        return default_upgrades


def save_upgrades(filename, data):
    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
            print("Upgrades saved.")
    except Exception as e:
        print(f"Error saving upgrades: {e}")


def run_bot():
    global bot_running
    process_name = "Unfair Flips.exe"

    print("--- Unfair Flips Bot Started ---")

    try:
        pm = Pymem(process_name)
        print(f"Process {process_name} found.")
    except Exception:
        print(f"ERROR: Process {process_name} not found. Make sure the game is running.")
        bot_running = False
        return

    try:
        # Looking for the specific Mono DLL
        module = module_from_name(pm.process_handle, "mono-2.0-bdwgc.dll").lpBaseOfDll
        print(f"DLL found, base address: {hex(module)}")
    except AttributeError:
        print("ERROR: Could not find mono-2.0-bdwgc.dll")
        bot_running = False
        return

    # Base offsets
    base_static_offset = 0x007F56C0
    offsets = [0x788, 0xB60]
    start_address = module + base_static_offset

    upgrades = load_upgrades("upgrades.json")
    print(f"Current upgrades: {upgrades}")

    # Button Coordinates (Make sure game window is in the correct position!)
    flip_button_cords = (307, 986)

    buttons = {
        "chance": (1609, 284),
        "speed": (1609, 485),
        "combo": (1609, 685),
        "worth": (1609, 893)
    }

    print("Starting loop... Press 'H' to stop.")

    while bot_running:
        money_addr = get_pointer_addr(pm, start_address, offsets)

        if money_addr:
            try:
                # Click the flip button
                gui.moveTo(flip_button_cords[0], flip_button_cords[1])
                gui.click()

                # Read money
                money = pm.read_int(money_addr)
                print(f"Address: {hex(money_addr)} | Money: {money}")

                # Create a copy to check for changes later
                previous_upgrades = upgrades.copy()

                # --- UPGRADE LOGIC ---
                def buy(name, level):
                    gui.moveTo(buttons[name][0], buttons[name][1])
                    gui.click()
                    upgrades[name] = level
                    print(f"Bought upgrade: {name} -> Level {level}")

                # Level 1 Phase
                if money >= 1:
                    if upgrades["speed"] == 0:
                        buy("speed", 1)
                    elif upgrades["chance"] == 0:
                        buy("chance", 1)
                    elif upgrades["combo"] == 0:
                        buy("combo", 1)

                # Level 2 Phase
                if money >= 10:
                    if upgrades["chance"] == 1:
                        buy("chance", 2)
                    elif upgrades["speed"] == 1:
                        buy("speed", 2)
                    elif upgrades["combo"] == 1:
                        buy("combo", 2)

                if money >= 25 and upgrades["worth"] == 0: buy("worth", 1)
                if money >= 100 and upgrades["worth"] == 1: buy("worth", 2)

                # Level 3 Phase
                if money >= 100:
                    if upgrades["chance"] == 2:
                        buy("chance", 3)
                    elif upgrades["speed"] == 2:
                        buy("speed", 3)
                    elif upgrades["combo"] == 2:
                        buy("combo", 3)

                if money >= 625 and upgrades["worth"] == 2: buy("worth", 3)

                # Level 4 Phase
                if money >= 1000:
                    if upgrades["chance"] == 3:
                        buy("chance", 4)
                    elif upgrades["speed"] == 3:
                        buy("speed", 4)
                    elif upgrades["combo"] == 3:
                        buy("combo", 4)

                if money >= 10000 and upgrades["worth"] == 3: buy("worth", 4)

                # Level 5 Phase
                if money >= 10000:
                    if upgrades["chance"] == 4:
                        buy("chance", 5)
                    elif upgrades["speed"] == 4:
                        buy("speed", 5)
                    elif upgrades["combo"] == 4:
                        buy("combo", 5)

                # High Level Phase
                if money >= 100000 and upgrades["chance"] == 5: buy("chance", 6)
                if money >= 1000000 and upgrades["chance"] == 6: buy("chance", 7)
                if money >= 10000000 and upgrades["chance"] == 7: buy("chance", 8)

                # Save if changed
                if upgrades != previous_upgrades:
                    save_upgrades("upgrades.json", upgrades)

                # Calculate delay based on speed level
                speed_delays = {0: 1.0, 1: 0.8, 2: 0.6, 3: 0.4, 4: 0.2, 5: 0.1}
                base_delay = speed_delays.get(upgrades["speed"], 0.1)

                time.sleep(1 + base_delay)

            except Exception as e:
                print(f"Runtime error: {e}")
        else:
            print("Waiting for valid memory address...")
            time.sleep(2)


def on_press(key):
    global bot_running
    try:
        k = key.char
    except AttributeError:
        k = key.name

    if k == "h":
        print("Stopping bot...")
        bot_running = False
        os._exit(0)

    if k == "enter":
        if not bot_running:
            bot_running = True
            threading.Thread(target=run_bot).start()
        else:
            print("Bot is already running!")


if __name__ == "__main__":
    print("Press 'Enter' to start the bot.")
    print("Press 'H' to stop.")

    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    listener.join()