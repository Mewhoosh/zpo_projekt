"""
PPO Training script for racing game.
Usage: Run in PyCharm or: python train.py
"""

from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback, BaseCallback
from stable_baselines3.common.vec_env import SubprocVecEnv, VecMonitor
from stable_baselines3.common.monitor import Monitor
from ai.racing_env import RacingEnv
import os
import numpy as np
import matplotlib.pyplot as plt


# === SETTINGS ===
SAVE_PATH = "models/v4"
TRACK_FILE = "tracks/test.png"
TOTAL_TIMESTEPS = 100000
N_ENVS = 8


class TrainingLogger(BaseCallback):
    """Logs rewards and checkpoints, saves plots."""

    def __init__(self, log_freq=8192, save_path=SAVE_PATH):
        super().__init__(verbose=1)
        self.log_freq = log_freq
        self.save_path = save_path
        self.episode_rewards = []
        self.episode_lengths = []
        self.episode_checkpoints = []
        self.log_timesteps = []
        self.log_rewards = []
        self.log_checkpoints = []

    def _on_step(self):
        infos = self.locals.get('infos', [])
        dones = self.locals.get('dones', [])

        for info, done in zip(infos, dones):
            if done:
                if 'episode' in info:
                    self.episode_rewards.append(info['episode']['r'])
                    self.episode_lengths.append(info['episode']['l'])
                if 'checkpoint' in info:
                    self.episode_checkpoints.append(info['checkpoint'])

        if self.num_timesteps % self.log_freq == 0 and len(self.episode_rewards) > 0:
            last_n = 50
            mean_rew = np.mean(self.episode_rewards[-last_n:])
            max_rew = np.max(self.episode_rewards[-last_n:])
            mean_len = np.mean(self.episode_lengths[-last_n:]) if self.episode_lengths else 0
            mean_cp = np.mean(self.episode_checkpoints[-last_n:]) if self.episode_checkpoints else 0
            max_cp = np.max(self.episode_checkpoints[-last_n:]) if self.episode_checkpoints else 0

            self.log_timesteps.append(self.num_timesteps)
            self.log_rewards.append(mean_rew)
            self.log_checkpoints.append(mean_cp)

            print(f"\n=== [{self.num_timesteps}] ===")
            print(f"  Reward: {mean_rew:.1f} (max: {max_rew:.1f})")
            print(f"  Checkpoints: {mean_cp:.2f} (max: {max_cp})")
            print(f"  Episode length: {mean_len:.0f}")

        return True

    def _on_training_end(self):
        """Save training plots."""
        if len(self.log_timesteps) < 2:
            return

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

        ax1.plot(self.log_timesteps, self.log_rewards, 'b-', linewidth=2)
        ax1.set_xlabel('Steps')
        ax1.set_ylabel('Mean Reward')
        ax1.set_title('Reward over training')
        ax1.grid(True)

        ax2.plot(self.log_timesteps, self.log_checkpoints, 'g-', linewidth=2)
        ax2.set_xlabel('Steps')
        ax2.set_ylabel('Mean Checkpoints')
        ax2.set_title('Checkpoints over training')
        ax2.grid(True)

        plt.tight_layout()
        plot_path = os.path.join(self.save_path, "training_plot.png")
        plt.savefig(plot_path, dpi=150)
        plt.close()
        print(f"\nPlot saved: {plot_path}")


def make_env(track_file):
    def _init():
        env = RacingEnv(track_file=track_file, render_mode=None)
        return Monitor(env)
    return _init


def train():
    os.makedirs(SAVE_PATH, exist_ok=True)

    env = SubprocVecEnv([make_env(TRACK_FILE) for _ in range(N_ENVS)])
    env = VecMonitor(env)

    checkpoint_callback = CheckpointCallback(
        save_freq=10000 // N_ENVS,
        save_path=SAVE_PATH,
        name_prefix="racing_ppo"
    )

    logger = TrainingLogger(log_freq=8192, save_path=SAVE_PATH)

    model = PPO(
        "MlpPolicy",
        env,
        learning_rate=0.0003,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.005,  # Less exploration over time
        verbose=1
    )

    print(f"Starting PPO training: {TOTAL_TIMESTEPS} steps")
    print(f"Parallel envs: {N_ENVS}")
    print(f"Save path: {SAVE_PATH}/")

    model.learn(
        total_timesteps=TOTAL_TIMESTEPS,
        callback=[checkpoint_callback, logger]
    )

    final_path = os.path.join(SAVE_PATH, "racing_ppo_final")
    model.save(final_path)
    print(f"\nTraining done! Model: {final_path}.zip")

    env.close()


if __name__ == "__main__":
    train()

