import gymnasium as gym
from gymnasium import spaces
import numpy as np

from core.track import Track
from core.track_loader import TrackLoader
from core.physics_engine import PhysicsEngine
from entities.ai_car import AICar


class RacingEnv(gym.Env):
    """
    Gymnasium environment for racing game.

    Observations (9 values):
        - 7 raycasts (distances to walls, normalized 0-1)
        - speed (normalized -1 to 1)
        - distance to next checkpoint (normalized 0-1)

    Actions (5 discrete):
        0: Nothing
        1: Gas
        2: Gas + Left
        3: Gas + Right
        4: Reverse

    Rewards:
        +200: Checkpoint crossed
        +1000 + time_bonus: Lap completed
        -5: Wall collision
        +progress: Getting closer to checkpoint
    """

    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 60}

    def __init__(self, track_file="tracks/test.png", render_mode=None, max_steps=800):
        super().__init__()

        self.render_mode = render_mode
        self.max_steps = max_steps
        self._current_step = 0
        self._steps_without_progress = 0
        self._max_steps_without_progress = 300

        # Load track
        loader = TrackLoader()
        track_data = loader.load_from_png(track_file)
        self._track = Track(track_data=track_data)

        # Physics
        self._physics = PhysicsEngine()

        # AI vehicle
        start_x, start_y = self._track.start_position
        self._car = AICar(start_x, start_y)
        self._car.set_angle(90)

        # Checkpoint tracking
        self._next_checkpoint = 0
        self._laps_completed = 0

        # Raycast range (longer = sees walls further away)
        self._max_raycast_distance = 500

        # Action space: 5 discrete
        self.action_space = spaces.Discrete(5)

        # Observation space: 7 raycasts + speed + checkpoint distance
        self.observation_space = spaces.Box(
            low=-1.0,
            high=1.0,
            shape=(9,),
            dtype=np.float32
        )

        # Pygame for rendering (lazy init)
        self._screen = None
        self._clock = None
        self._renderer = None

    def _get_observation(self):
        """Returns normalized observations."""
        # Raycasts (7 values, normalized 0-1)
        distances, _ = self._car.get_raycasts(self._track, self._max_raycast_distance)
        normalized_rays = [d / self._max_raycast_distance for d in distances]

        # Speed (normalized -1 to 1)
        normalized_speed = self._car.speed / self._car.MAX_SPEED

        # Distance to next checkpoint
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
        self._steps_without_progress = 0

        return self._get_observation(), self._get_info()

    def step(self, action):
        """
        Wykonuje jeden krok symulacji.

        Args:
            action: Akcja do wykonania (0-7)

        Returns:
            observation: Nowe obserwacje
            reward: Nagroda za ten krok
            terminated: Czy epizod się skończył (ukończono okrążenie)
            truncated: Czy epizod został przerwany (max kroków, brak postępu)
            info: Dodatkowe informacje
        """
        self._current_step += 1
        self._steps_without_progress += 1

        # Zapisz starą pozycję i odległość do checkpointu
        old_x, old_y = self._car.x, self._car.y
        old_dist_to_cp = self._get_distance_to_checkpoint()

        # Wykonaj akcję
        self._car.set_action(action)
        self._car.update(1/60)  # dt = 1/60

        # Nowa odległość do checkpointu
        new_dist_to_cp = self._get_distance_to_checkpoint()

        # Oblicz przebyty dystans
        distance_moved = np.sqrt((self._car.x - old_x)**2 + (self._car.y - old_y)**2)

        # === REWARD SYSTEM ===
        reward = 0.0
        had_collision = False

        # Check collision first
        if self._physics.handle_collision(self._car, self._track):
            reward -= 5
            had_collision = True

        # Reward for getting closer to checkpoint
        if old_dist_to_cp is not None and new_dist_to_cp is not None:
            progress = old_dist_to_cp - new_dist_to_cp
            reward += progress * 1.0

        # Reward for driving forward
        if self._car.speed > 0.5:
            reward += 0.05

        # Penalty for reversing without reason
        if action == 4 and not had_collision:
            reward -= 0.1

        terminated = False
        truncated = False

        # Check checkpoint
        if self._track.check_checkpoint_crossing(
            old_x, old_y, self._car.x, self._car.y, self._next_checkpoint
        ):
            reward += 200  # Checkpoint reward
            self._next_checkpoint += 1
            self._steps_without_progress = 0

        # Check finish line
        if self._next_checkpoint >= self._track.total_checkpoints:
            if self._track.check_finish_line_crossing(old_x, old_y, self._car.x, self._car.y):
                # Time bonus: faster lap = more points
                time_bonus = 500 * (self.max_steps - self._current_step) / self.max_steps
                reward += 1000 + time_bonus
                self._laps_completed += 1
                self._next_checkpoint = 0
                self._track.reset_checkpoints()
                self._steps_without_progress = 0

        # Check no-progress limit
        if self._steps_without_progress >= self._max_steps_without_progress:
            truncated = True

        # Check max steps
        if self._current_step >= self.max_steps:
            truncated = True

        return self._get_observation(), reward, terminated, truncated, self._get_info()

    def _get_distance_to_checkpoint(self):
        """Zwraca odległość do następnego checkpointu."""
        if self._next_checkpoint < len(self._track.checkpoints):
            cp = self._track.checkpoints[self._next_checkpoint]
            cp_x = (cp['x1'] + cp['x2']) / 2
            cp_y = (cp['y1'] + cp['y2']) / 2
            return np.sqrt((self._car.x - cp_x)**2 + (self._car.y - cp_y)**2)
        return None

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
