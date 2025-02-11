import tkinter as tk
from tkinter import font as tkFont
import customtkinter as ctk
import time
import colorsys
# import mouse_capture  # Module gérant la capture souris (à activer si nécessaire)
import keyboard_capture  # Module gérant la capture clavier
from config import FONT_COLOR, FONT_FAMILY, FONT_SIZE, DISPLAY_DURATION, MIN_FONT_SIZE, MAX_FONT_SIZE
from animate_dots import DotAnimator  # Module d'animation pour l'affichage principal
import platform


# --- Configuration de CustomTkinter ---
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# =============================================================================
# Partie 1 : Fenêtre principale (capture clavier & affichage)
# =============================================================================

root = ctk.CTk()
root.title("Touches pressées")
root.overrideredirect(True)
root.attributes("-topmost", True)


if platform.system() == "Windows":
    root.attributes("-transparentcolor", "black")  # Fonctionne uniquement sous Windows
else:
    root.attributes("-alpha", 0.0)  # Ajuste l'opacité sous Linux/macOS (0.0 = complètement transparent, 1.0 = opaque)

# Dimensions et positionnement de la fenêtre principale
window_width, window_height = 450, 100
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_position = 0
y_position = screen_height - window_height
root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

# Canevas d'affichage principal
canvas = tk.Canvas(root, width=window_width, height=window_height, bg="black", highlightthickness=0)
canvas.pack()

# Police d'affichage
display_font = tkFont.Font(family=FONT_FAMILY, size=FONT_SIZE)
text_item = canvas.create_text(window_width // 2, window_height // 2,
                               text="Saisie désactivée",
                               fill=FONT_COLOR,
                               font=display_font)

# Animation pour l'affichage lorsque aucune saisie n'est active
animator = DotAnimator(interval=500)

def update_canvas():
    current_time = time.time()
    keys_to_remove = []
    # Gestion des touches capturées
    for key_str, release_time in list(keyboard_capture.pressed_keys.items()):
        if release_time is not None:
            elapsed = (current_time - release_time) * 1000  # en millisecondes
            if elapsed >= DISPLAY_DURATION:
                keys_to_remove.append(key_str)
    for key_str in keys_to_remove:
        del keyboard_capture.pressed_keys[key_str]

    if not keyboard_capture.capture_active:
        display_text = "Saisie désactivée"
    elif keyboard_capture.pressed_keys:
        # Tri pour afficher Ctrl, Shift, Alt en priorité
        keys_list = sorted(keyboard_capture.pressed_keys.keys(),
                           key=lambda k: {"Ctrl": 0, "Shift": 1, "Alt": 2}.get(k, 99))
        display_text = "+".join(keys_list)
    else:
        # Affichage de l'animation par défaut
        display_text = animator.get_state()

    canvas.itemconfig(text_item, text=display_text, fill=FONT_COLOR, font=display_font)
    root.after(50, update_canvas)

update_canvas()

# --- Drag & Drop pour déplacer la fenêtre principale ---
def start_drag(event):
    root.startX = event.x
    root.startY = event.y

def do_drag(event):
    new_x = event.x_root - root.startX
    new_y = event.y_root - root.startY
    root.geometry(f"+{new_x}+{new_y}")

root.bind("<ButtonPress-1>", start_drag)
root.bind("<B1-Motion>", do_drag)

# =============================================================================
# Partie 2 : Fenêtre de paramètres (police, couleur, taille, opacité, etc.)
# =============================================================================

settings_win = ctk.CTkToplevel(root)
settings_win.title("Paramètres d'affichage")
settings_win.geometry("500x570")
settings_win.attributes("-topmost", True)
settings_win.lift()
settings_win.grid_columnconfigure(0, weight=1)
settings_win.grid_columnconfigure(1, weight=1)

# -- Ligne 0 : Choix de la police --
common_fonts = ["Arial", "Helvetica", "Times New Roman", "Courier New", "Verdana", "Georgia", "ROBOTO", "Segoe UI"]

label_font = ctk.CTkLabel(settings_win, text="Police :")
label_font.grid(row=0, column=0, padx=5, pady=5, sticky="e")
font_family_var = ctk.StringVar(value=FONT_FAMILY)

def update_font_family(selected_font):
    global FONT_FAMILY
    FONT_FAMILY = selected_font
    display_font.config(family=FONT_FAMILY)

combo_font = ctk.CTkComboBox(settings_win, values=common_fonts, variable=font_family_var,
                             state="readonly", command=update_font_family)
combo_font.grid(row=0, column=1, padx=5, pady=5, sticky="w")

# -- Ligne 1 : Choix de la couleur via un color picker graphique --
label_color = ctk.CTkLabel(settings_win, text="Choix de couleur", anchor="w")
label_color.grid(row=1, column=0, padx=5, pady=5, sticky="e")

color_picker_frame = ctk.CTkFrame(settings_win, fg_color="#1a1a1a", width=320, height=220, corner_radius=10)
color_picker_frame.grid(row=1, column=1, padx=5, pady=5, sticky="w")
color_picker_frame.grid_propagate(False)  # Conserver la taille fixe

# Canevas pour le dégradé de teintes (fixe, avec luminance 0.5)
canvas_width = 300
canvas_height = 50
hue_canvas = tk.Canvas(color_picker_frame, width=canvas_width, height=canvas_height, highlightthickness=0)
hue_canvas.pack(pady=10)

def update_hue_gradient():
    """Redessine le dégradé sur hue_canvas avec une luminance fixe (0.5)."""
    hue_canvas.delete("all")
    fixed_luminance = 0.5  # Luminance constante pour le dégradé
    for x in range(canvas_width):
        hue = x / canvas_width  # teinte entre 0 et 1
        r, g, b = colorsys.hls_to_rgb(hue, fixed_luminance, 1)
        hex_color = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
        hue_canvas.create_line(x, 0, x, canvas_height, fill=hex_color)

update_hue_gradient()

# Variable globale pour la teinte sélectionnée
selected_hue = 0.0

def select_hue(event):
    """Sélectionne la teinte en fonction de la position horizontale cliquée sur le canevas."""
    global selected_hue
    x = event.x
    x = max(0, min(canvas_width, x))
    selected_hue = x / canvas_width
    update_color_preview()

hue_canvas.bind("<Button-1>", select_hue)

# Zone d'aperçu de la couleur
color_preview = tk.Label(color_picker_frame, text="Aperçu", bg="#ff0000", fg="white", width=20, height=2)
color_preview.pack(pady=10)

def update_color_preview():
    """
    Combine la teinte sélectionnée et la luminance du slider pour générer la couleur finale,
    et met à jour la zone d'aperçu.
    """
    l = lightness_slider.get()  # Valeur de luminance (0.01 à 1)
    r, g, b = colorsys.hls_to_rgb(selected_hue, l, 1)
    hex_color = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
    color_preview.configure(bg=hex_color)
    global FONT_COLOR
    FONT_COLOR = hex_color

# Curseur pour ajuster la luminance (affecte uniquement la couleur d'aperçu)
lightness_label = ctk.CTkLabel(color_picker_frame, text="Luminance Noir/Blanc)")
lightness_label.pack(pady=(10, 0))
lightness_slider = ctk.CTkSlider(
    color_picker_frame,
    from_=0.01,
    to=1,
    number_of_steps=100,
    command=lambda value: update_color_preview()
)
lightness_slider.set(0.5)
lightness_slider.pack(pady=5, fill="x", padx=20)

# Appel initial
update_color_preview()


# -- Ligne pour la taille du texte --
label_size = ctk.CTkLabel(settings_win, text="Taille :")
label_size.grid(row=2, column=0, padx=5, pady=5, sticky="e")

frame_size = ctk.CTkFrame(settings_win)
frame_size.grid(row=2, column=1, padx=5, pady=5, sticky="w")

def increase_font_size():
    global FONT_SIZE
    if FONT_SIZE < MAX_FONT_SIZE:
        FONT_SIZE += 2
        display_font.config(size=FONT_SIZE)

def decrease_font_size():
    global FONT_SIZE
    if FONT_SIZE > MIN_FONT_SIZE:
        FONT_SIZE -= 2
        display_font.config(size=FONT_SIZE)

btn_increase = ctk.CTkButton(frame_size, text="Grande", command=increase_font_size)
btn_increase.grid(row=0, column=0, padx=2, pady=2)
btn_decrease = ctk.CTkButton(frame_size, text="Petite", command=decrease_font_size)
btn_decrease.grid(row=1, column=0, padx=2, pady=2)

# -- Ligne : Réglage de la durée d'affichage --
def update_display_duration(value):
    global DISPLAY_DURATION
    DISPLAY_DURATION = int(value)
    duration_label.configure(text=f"{DISPLAY_DURATION} ms")

label_duration = ctk.CTkLabel(settings_win, text="Durée d'affichage (ms) :")
label_duration.grid(row=5, column=0, padx=5, pady=5, sticky="e")
slider_duration = ctk.CTkSlider(settings_win, from_=100, to=2000, number_of_steps=19, command=update_display_duration)
slider_duration.set(DISPLAY_DURATION)
slider_duration.grid(row=5, column=1, padx=5, pady=5, sticky="w")
duration_label = ctk.CTkLabel(settings_win, text=f"{DISPLAY_DURATION} ms")
duration_label.grid(row=6, column=1, padx=5, pady=5, sticky="w")

# -- Ligne : Curseur pour l'opacité de l'affichage --
opacity_label = ctk.CTkLabel(settings_win, text="Opacité de l'affichage", anchor="w")
opacity_label.grid(row=7, column=0, padx=5, pady=5, sticky="e")
opacity_slider = ctk.CTkSlider(settings_win, from_=0.0, to=1.0, number_of_steps=100)
opacity_slider.set(1.0)
opacity_slider.grid(row=7, column=1, padx=5, pady=5, sticky="w")

def update_opacity(value):
    try:
        alpha = float(value)
        root.attributes("-alpha", alpha)
    except ValueError:
        pass

opacity_slider.configure(command=update_opacity)

# -- Ligne : Bouton pour activer/désactiver la capture clavier --
def toggle_capture():
    keyboard_capture.capture_active = not keyboard_capture.capture_active
    if keyboard_capture.capture_active:
        btn_toggle.configure(text="Arrêter la saisie")
    else:
        btn_toggle.configure(text="Démarrer la saisie")
        keyboard_capture.pressed_keys.clear()

btn_toggle = ctk.CTkButton(settings_win, text="Démarrer la saisie", command=toggle_capture)
btn_toggle.grid(row=8, column=0, columnspan=2, padx=5, pady=5)

# -- Ligne : Bouton pour quitter l'application --
def quitter():
    try:
        keyboard_capture.capture_active = False
    except Exception as e:
        print("Erreur lors de l'arrêt du listener clavier :", e)
    root.destroy()

btn_quit = ctk.CTkButton(settings_win, text="Quitter", command=quitter)
btn_quit.grid(row=9, column=0, columnspan=2, padx=5, pady=5)

# =============================================================================
# Partie 3 : Fenêtre de capture souris ("ui_mouse")
# =============================================================================

# mouse_win = ctk.CTkToplevel(root)
# root.attributes("-topmost", True)
# mouse_win.title("Capture de souris - Joystick")
# mouse_win.geometry("300x400")
#
#
# # --- Canevas pour simuler un joystick ---
# canvas_width_mouse = 200
# canvas_height_mouse = 200
# joystick_canvas = tk.Canvas(mouse_win, width=canvas_width_mouse, height=canvas_height_mouse,
#                             bg="lightgrey", highlightthickness=0)
# joystick_canvas.pack(pady=10)
#
# # Cercle extérieur (zone du joystick)
# padding = 5
# joystick_canvas.create_oval(padding, padding,
#                             canvas_width_mouse - padding,
#                             canvas_height_mouse - padding,
#                             outline="black")
#
# center_x = canvas_width_mouse // 2
# center_y = canvas_height_mouse // 2
#
# dot_radius = 5
# dot = joystick_canvas.create_oval(center_x - dot_radius, center_y - dot_radius,
#                                   center_x + dot_radius, center_y + dot_radius,
#                                   fill="red")
#
# # --- Boutons indiquant l'état des clics souris ---
# btn_frame = ctk.CTkFrame(mouse_win)
# btn_frame.pack(pady=10)
#
# btn_left = ctk.CTkButton(btn_frame, text="Gauche", width=80)
# btn_left.grid(row=0, column=0, padx=5, pady=5)
# btn_middle = ctk.CTkButton(btn_frame, text="Centre", width=80)
# btn_middle.grid(row=1, column=0, padx=5, pady=5)
# btn_right = ctk.CTkButton(btn_frame, text="Droit", width=80)
# btn_right.grid(row=2, column=0, padx=5, pady=5)
#
# # Variables pour le suivi du mouvement
# initial_mouse_x = None
# initial_mouse_y = None
# max_disp = 100  # déplacement maximal (en pixels)
#
# def update_mouse_ui():
#     global initial_mouse_x, initial_mouse_y
#     # Mise à jour de la position du "dot" sur le joystick en fonction des mouvements
#     if mouse_capture.mouse_movements:
#         last_move = mouse_capture.mouse_movements[-1]
#         current_x = last_move['x']
#         current_y = last_move['y']
#         if initial_mouse_x is None or initial_mouse_y is None:
#             initial_mouse_x = current_x
#             initial_mouse_y = current_y
#         dx = current_x - initial_mouse_x
#         dy = current_y - initial_mouse_y
#         dx = max(-max_disp, min(dx, max_disp))
#         dy = max(-max_disp, min(dy, max_disp))
#         new_dot_x = center_x + dx
#         new_dot_y = center_y + dy
#         joystick_canvas.coords(dot,
#                                new_dot_x - dot_radius, new_dot_y - dot_radius,
#                                new_dot_x + dot_radius, new_dot_y + dot_radius)
#     # Mise à jour de l'état des boutons en fonction de l'état actuel des clics souris
#     state = mouse_capture.current_mouse_state  # Ce dictionnaire doit être mis à jour dans mouse_capture.py
#     if state.get("Button.left", False):
#         btn_left.configure(fg_color="green")
#     else:
#         btn_left.configure(fg_color="gray")
#     if state.get("Button.middle", False):
#         btn_middle.configure(fg_color="green")
#     else:
#         btn_middle.configure(fg_color="gray")
#     if state.get("Button.right", False):
#         btn_right.configure(fg_color="green")
#     else:
#         btn_right.configure(fg_color="gray")
#     mouse_win.after(50, update_mouse_ui)
#
# # Démarrer l'écouteur de souris (assurez-vous que mouse_capture.py est correctement configuré)
# mouse_capture.start_mouse_listener()
# print("Listener de souris démarré depuis l'interface.")
# btn_left = ctk.CTkButton(btn_frame, text="Gauche", width=80, hover_color="gray")
# btn_middle = ctk.CTkButton(btn_frame, text="Centre", width=80, hover_color="gray")
# btn_right = ctk.CTkButton(btn_frame, text="Droit", width=80, hover_color="gray")
#
# update_mouse_ui()

# =============================================================================
# Lancement de l'interface
# =============================================================================

def run_ui():
    root.mainloop()

if __name__ == "__main__":
    run_ui()
