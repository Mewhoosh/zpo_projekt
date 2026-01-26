from entities.vehicle import Vehicle


class AICar(Vehicle):
    """Pojazd sterowany przez AI - nie czyta inputu z klawiatury."""

    def __init__(self, x, y):
        super().__init__(x, y)
        self._color = (255, 100, 0)  # Pomarańczowy dla AI
        self._current_action = 0

    def set_action(self, action):
        """
        Ustawia akcję do wykonania.
        Akcje:
            0: Nic
            1: Gaz
            2: Gaz + Lewo
            3: Gaz + Prawo
            4: Hamulec
            5: Cofanie
            6: Cofanie + Lewo
            7: Cofanie + Prawo
        """
        self._current_action = action

    def handle_input(self):
        """Wykonuje akcję ustawioną przez AI."""
        action = self._current_action

        if action == 1:  # Gaz
            self.accelerate(self.ACCELERATION)
        elif action == 2:  # Gaz + Lewo
            self.accelerate(self.ACCELERATION)
            if abs(self.speed) > 0.5:
                direction = 1 if self.speed > 0 else -1
                self.rotate(-self.ROTATION_SPEED * direction)
        elif action == 3:  # Gaz + Prawo
            self.accelerate(self.ACCELERATION)
            if abs(self.speed) > 0.5:
                direction = 1 if self.speed > 0 else -1
                self.rotate(self.ROTATION_SPEED * direction)
        elif action == 4:  # Hamulec
            self.accelerate(-self.ACCELERATION * 0.5)
        elif action == 5:  # Cofanie
            self.accelerate(-self.ACCELERATION * 0.5)
        elif action == 6:  # Cofanie + Lewo
            self.accelerate(-self.ACCELERATION * 0.5)
            if abs(self.speed) > 0.5:
                direction = 1 if self.speed > 0 else -1
                self.rotate(-self.ROTATION_SPEED * direction)
        elif action == 7:  # Cofanie + Prawo
            self.accelerate(-self.ACCELERATION * 0.5)
            if abs(self.speed) > 0.5:
                direction = 1 if self.speed > 0 else -1
                self.rotate(self.ROTATION_SPEED * direction)
