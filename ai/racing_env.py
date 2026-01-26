import gymnasium as gym
from gymnasium import spaces
import numpy as np

from core.track import Track
from core.track_loader import TrackLoader
from core.physics_engine import PhysicsEngine
from entities.ai_car import AICar


class RacingEnv(gym.Env):
    """
    Środowisko Gymnasium dla gry wyścigowej.

    Obserwacje (9 wartości):
        - 7 raycastów (odległości do ścian, znormalizowane 0-1)
        - prędkość (znormalizowana -1 do 1)
        - odległość do następnego checkpointu (znormalizowana 0-1)

    Akcje (8 dyskretnych):
        0: Nic
        1: Gaz
        2: Gaz + Lewo
        3: Gaz + Prawo
        4: Hamulec
        5: Cofanie
        6: Cofanie + Lewo
        7: Cofanie + Prawo

    Nagrody:
        +100: Przejechanie checkpointu
        +500: Ukończenie okrążenia
        -50: Kolizja ze ścianą
        -0.1: Kara za każdy krok (żeby się spieszył)
        +0.1 * prędkość: Nagroda za jazdę
    """

    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 60}

    def __init__(self, track_file="tracks/test.png", render_mode=None, max_steps=2000):
        super().__init__()

        self.render_mode = render_mode
        self.max_steps = max_steps
        self._current_step = 0

        # Ładowanie toru
        loader = TrackLoader()
        track_data = loader.load_from_png(track_file)
        self._track = Track(track_data=track_data)

        # Fizyka
        self._physics = PhysicsEngine()

        # Pojazd AI
        start_x, start_y = self._track.start_position
        self._car = AICar(start_x, start_y)
        self._car.set_angle(90)

        # Śledzenie checkpointów
        self._next_checkpoint = 0
        self._laps_completed = 0

        # Stałe dla normalizacji
        self._max_raycast_distance = 300

        # Przestrzeń akcji: 8 dyskretnych akcji
        self.action_space = spaces.Discrete(8)

        # Przestrzeń obserwacji: 7 raycastów + prędkość + odległość do checkpointu
        self.observation_space = spaces.Box(
            low=-1.0,
            high=1.0,
            shape=(9,),
            dtype=np.float32
        )

        # Pygame dla renderowania (inicjalizowane leniwie)
        self._screen = None
        self._clock = None
        self._renderer = None

    def _get_observation(self):
        """Zwraca znormalizowane obserwacje."""
        # Raycasty (7 wartości, znormalizowane 0-1)
        distances, _ = self._car.get_raycasts(self._track, self._max_raycast_distance)
        normalized_rays = [d / self._max_raycast_distance for d in distances]

        # Prędkość (znormalizowana -1 do 1)
        normalized_speed = self._car.speed / self._car.MAX_SPEED

        # Odległość do następnego checkpointu (uproszczone - używamy pozycji)
        if self._next_checkpoint < len(self._track.checkpoints):
            cp = self._track.checkpoints[self._next_checkpoint]
            cp_x = (cp['x1'] + cp['x2']) / 2
            cp_y = (cp['y1'] + cp['y2']) / 2
            dist = np.sqrt((self._car.x - cp_x)**2 + (self._car.y - cp_y)**2)
            max_dist = np.sqrt(self._track._width**2 + self._track._height**2)
            normalized_cp_dist = min(dist / max_dist, 1.0)
        else:
            normalized_cp_dist = 0.0

        obs = np.array(normalized_rays + [normalized_speed, normalized_cp_dist], dtype=np.float32)
        return obs

    def _get_info(self):
        """Zwraca dodatkowe informacje."""
        return {
            "checkpoint": self._next_checkpoint,
            "total_checkpoints": self._track.total_checkpoints,
            "laps": self._laps_completed,
            "speed": self._car.speed,
            "position": (self._car.x, self._car.y)
        }

    def reset(self, seed=None, options=None):
        """Resetuje środowisko do stanu początkowego."""
        super().reset(seed=seed)

        # Reset pozycji
        start_x, start_y = self._track.start_position
        self._car.set_position(start_x, start_y)
        self._car.set_angle(90)
        self._car.accelerate(-self._car.speed)  # Zeruj prędkość

        # Reset checkpointów
        self._next_checkpoint = 0
        self._laps_completed = 0
        self._track.reset_checkpoints()

        # Reset kroków
        self._current_step = 0

        return self._get_observation(), self._get_info()

    def step(self, action):
        """
        Wykonuje jeden krok symulacji.

        Args:
            action: Akcja do wykonania (0-4)

        Returns:
            observation: Nowe obserwacje
            reward: Nagroda za ten krok
            terminated: Czy epizod się skończył (ukończono okrążenie)
            truncated: Czy epizod został przerwany (max kroków, kolizja)
            info: Dodatkowe informacje
        """
        self._current_step += 1

        # Zapisz starą pozycję
        old_x, old_y = self._car.x, self._car.y

        # Wykonaj akcję
        self._car.set_action(action)
        self._car.update(1/60)  # dt = 1/60

        # Inicjalizuj nagrodę
        reward = -0.1  # Kara za czas
        reward += 0.1 * abs(self._car.speed)  # Nagroda za prędkość

        terminated = False
        truncated = False

        # Sprawdź kolizję
        if self._physics.handle_collision(self._car, self._track):
            reward -= 50  # Kara za kolizję

        # Sprawdź checkpoint
        if self._track.check_checkpoint_crossing(
            old_x, old_y, self._car.x, self._car.y, self._next_checkpoint
        ):
            reward += 100  # Nagroda za checkpoint
            self._next_checkpoint += 1

        # Sprawdź linię mety
        if self._next_checkpoint >= self._track.total_checkpoints:
            if self._track.check_finish_line_crossing(old_x, old_y, self._car.x, self._car.y):
                reward += 500  # Nagroda za okrążenie
                self._laps_completed += 1
                self._next_checkpoint = 0
                self._track.reset_checkpoints()
                terminated = True  # Kończymy epizod po okrążeniu

        # Sprawdź limit kroków
        if self._current_step >= self.max_steps:
            truncated = True

        return self._get_observation(), reward, terminated, truncated, self._get_info()

    def render(self):
        """Renderuje aktualny stan gry."""
        if self.render_mode is None:
            return

        # Inicjalizacja pygame przy pierwszym renderowaniu
        if self._screen is None:
            import pygame
            from core.renderer import Renderer

            pygame.init()
            self._screen = pygame.display.set_mode((self._track._width, self._track._height))
            pygame.display.set_caption("Racing AI Training")
            self._clock = pygame.time.Clock()
            self._renderer = Renderer(self._screen)

        import pygame

        # Obsługa zdarzeń (żeby okno nie zamarzło)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()
                return

        # Renderowanie
        self._renderer.clear(self._track.background_color)
        self._renderer.draw_track(self._track, show_checkpoints=True)
        self._renderer.draw_vehicle(self._car)

        # Rysuj raycasty
        _, endpoints = self._car.get_raycasts(self._track)
        self._renderer.draw_raycasts(self._car, endpoints)

        # Info
        self._renderer.draw_text(f"Step: {self._current_step}", 10, 10)
        self._renderer.draw_text(f"Checkpoint: {self._next_checkpoint}/{self._track.total_checkpoints}", 10, 45)
        self._renderer.draw_text(f"Laps: {self._laps_completed}", 10, 80)

        self._renderer.update_display()
        self._clock.tick(60)

    def close(self):
        """Zamyka środowisko."""
        if self._screen is not None:
            import pygame
            pygame.quit()
            self._screen = None
