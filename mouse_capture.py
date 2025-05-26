import mouse

capture_active = False
click_callback = None
scroll_callback = None  # Ajout pour gérer la molette
release_callback = None  # Ajout du callback pour gérer les relâchements de clics

def set_release_callback(callback):
    """ Associe une fonction pour gérer le relâchement des boutons souris """
    global release_callback
    release_callback = callback


def on_mouse_event(event):
    """ Capture TOUS les événements de clics (sans filtrer les doubles-clics) """

    if isinstance(event, mouse.ButtonEvent):
        print(f"[DEBUG] ButtonEvent détecté : {event}")

        if event.event_type == "down":  # Capture tous les clics (y compris doubles)
            print(f"[DEBUG] Clic enfoncé : {event.button}")
            if click_callback:
                click_callback(event.button)

        elif event.event_type == "up":  # Capture tous les relâchements
            print(f"[DEBUG] Clic relâché : {event.button}")
            if release_callback:
                release_callback(event.button)

    elif isinstance(event, mouse.WheelEvent):
        print(f"[DEBUG] Scroll détecté {event.delta}")
        if scroll_callback:
            scroll_callback(event.delta)


def start_mouse_listener():
    """ Active la capture des événements souris si ce n'est pas déjà fait """
    global capture_active
    if not capture_active:
        capture_active = True
        mouse.hook(on_mouse_event)
        print("[INFO] Listener de souris démarré")



def stop_capture():
    """ Désactive la capture des événements souris """
    global capture_active
    capture_active = False
    mouse.unhook_all()
    print("[INFO] Capture souris désactivée")


def set_click_callback(callback):
    """ Associe une fonction pour gérer les clics souris """
    global click_callback
    click_callback = callback


def set_scroll_callback(callback):
    """ Associe une fonction pour gérer le scroll """
    global scroll_callback
    scroll_callback = callback
