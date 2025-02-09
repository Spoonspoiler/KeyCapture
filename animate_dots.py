# animate_dots.py
import time

class DotAnimator:
    def __init__(self, interval=500):
        """
        interval : temps en millisecondes entre chaque changement d'état.
        """
        self.interval = interval / 1000.0  # conversion en secondes
        self.last_update = time.time()
        self.states = ["", ".", "..", "..."]
        self.index = 0

    def get_state(self):
        """Retourne l'état courant des points et met à jour l'animation selon l'intervalle."""
        current_time = time.time()
        if current_time - self.last_update >= self.interval:
            self.index = (self.index + 1) % len(self.states)
            self.last_update = current_time
        return self.states[self.index]
