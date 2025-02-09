# main.py
from ui import run_ui
from keyboard_capture import listener

def main():
    try:
        run_ui()
    finally:
        listener.stop()

if __name__ == "__main__":
    main()
