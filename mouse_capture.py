# mouse_capture.py
import time
from pynput import mouse

current_mouse_state = {
    "Button.left": False,
    "Button.middle": False,
    "Button.right": False
}


mouse_movements = []

def on_click(x, y, button, pressed):
    current_mouse_state[str(button)] = pressed
    print(f"[on_click] {button} {'pressé' if pressed else 'relâché'} en ({x}, {y})", flush=True)

def on_move(x, y):
    mouse_movements.append({'x': x, 'y': y, 'timestamp': time.time()})
    print(f"[on_move] Position: ({x}, {y})", flush=True)

def on_scroll(x, y, dx, dy):
    print(f"[on_scroll] Position: ({x}, {y}), dx: {dx}, dy: {dy}", flush=True)

mouse_listener = None

def start_mouse_listener():
    global mouse_listener
    if mouse_listener is None:
        mouse_listener = mouse.Listener(
            on_click=on_click,
            on_move=on_move,
            on_scroll=on_scroll,
            daemon=True
        )
        mouse_listener.start()
        print("Écouteur de souris démarré.", flush=True)

def stop_mouse_listener():
    global mouse_listener
    if mouse_listener is not None:
        mouse_listener.stop()
        mouse_listener = None
        print("Écouteur de souris arrêté.", flush=True)
