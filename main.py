import sys
import os

# add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from core.game_engine import GameEngine


def main():
    # track_file = "tracks/my_track.png"
    # track_file = "tracks/test_track.png"
    # track_file = "tracks/play_track.png"
    track_file = "tracks/test.png"
    game = GameEngine(track_file=track_file)
    game.run()


if __name__ == "__main__":
    main()
