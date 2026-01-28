from entities.vehicle import Vehicle


class AICar(Vehicle):
    """Pojazd sterowany przez AI."""

    def __init__(self, x, y):
        super().__init__(x, y)
        self._color = (255, 100, 0)  # Pomarańczowy dla AI
        self._current_action = 0

    def set_action(self, action):
        """
        Ustawia akcję do wykonania.

        Akcje (0-4):
            0: Nic
            1: Gaz
            2: Gaz + Lewo
            3: Gaz + Prawo
            4: Cofanie
        """
        self._current_action = int(action)

    def handle_input(self):
        """Wykonuje akcję ustawioną przez AI."""
        action = self._current_action

        if action == 1:  # Gaz
            self.accelerate(self.ACCELERATION)
        elif action == 2:  # Gaz + Lewo
            self.accelerate(self.ACCELERATION)
            if abs(self.speed) > 0.5:
                self.rotate(-self.ROTATION_SPEED)
        elif action == 3:  # Gaz + Prawo
            self.accelerate(self.ACCELERATION)
            if abs(self.speed) > 0.5:
                self.rotate(self.ROTATION_SPEED)
        elif action == 4:  # Cofanie
            self.accelerate(-self.ACCELERATION)
