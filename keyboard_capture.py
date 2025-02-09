# keyboard_capture.py
import time
from pynput import keyboard

capture_active = False
pressed_keys = {}

def key_to_str(key):
    try:
        if key.char is not None:
            if ord(key.char) < 32:
                letter = chr(ord(key.char) + 96)
                return letter.upper()
            else:
                return key.char.upper()
    except Exception:
        pass
    key_str = str(key).replace("Key.", "")
    if key_str.lower().startswith("ctrl"):
        return "Ctrl"
    elif key_str.lower().startswith("shift"):
        return "Shift"
    elif key_str.lower().startswith("alt"):
        return "Alt"
    else:
        return key_str.capitalize()

def on_press(key):
    if not capture_active:
        return
    key_str = key_to_str(key)
    if key_str and key_str not in pressed_keys:
        pressed_keys[key_str] = None

def on_release(key):
    if not capture_active:
        return
    key_str = key_to_str(key)
    if key_str in pressed_keys and pressed_keys[key_str] is None:
        pressed_keys[key_str] = time.time()

listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()
