"""
Watch trained agent driving.
Usage: Run in PyCharm or: python watch.py
"""

from stable_baselines3 import PPO
from ai.racing_env import RacingEnv
import pygame


# === SETTINGS ===
MODEL_PATH = "models/v3/racing_ppo_final.zip"
TRACK_PATH = "tracks/test.png"


def main():
    print(f"Model: {MODEL_PATH}")
    print(f"Track: {TRACK_PATH}")

    model = PPO.load(MODEL_PATH)
    env = RacingEnv(track_file=TRACK_PATH, render_mode="human", max_steps=999999)

    obs, info = env.reset()
    env.render()  # Initialize pygame

    pygame.font.init()
    font = pygame.font.Font(None, 36)

    total_laps = 0
    running = True
    clock = pygame.time.Clock()

    print("\n=== AGENT RUNNING ===")
    print("ESC = quit\n")

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        if not running:
            break

        action, _ = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)

        # Count laps
        current_laps = info.get('laps', 0)
        if current_laps > total_laps:
            total_laps = current_laps
            print(f"  Lap {total_laps} completed!")

        env.render()

        # Stats on screen
        if env._screen:
            cp = info.get('checkpoint', 0)
            total_cp = info.get('total_checkpoints', 3)
            text = f"Laps: {total_laps} | CP: {cp}/{total_cp} | ESC=quit"
            text_surface = font.render(text, True, (255, 255, 255))
            bg = pygame.Rect(5, 5, text_surface.get_width() + 10, 30)
            pygame.draw.rect(env._screen, (0, 0, 0), bg)
            env._screen.blit(text_surface, (10, 10))
            pygame.display.flip()

        clock.tick(60)

    env.close()
    print(f"\nDone. Laps: {total_laps}")


if __name__ == "__main__":
    main()

