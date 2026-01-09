import os
from core.track_loader import TrackLoader

def preprocess_all_tracks():
    """Process all PNG tracks and create cache files."""
    tracks_dir = "tracks"

    if not os.path.exists(tracks_dir):
        print("No tracks directory found!")
        return

    loader = TrackLoader()
    tracks = [f for f in os.listdir(tracks_dir) if f.endswith('.png')]

    if not tracks:
        print("No PNG tracks found!")
        return

    print(f"Found {len(tracks)} tracks to process...")
    print("-" * 50)

    for track in tracks:
        filepath = os.path.join(tracks_dir, track)
        print(f"\nProcessing: {track}")

        try:
            loader.load_from_png(filepath)
            print(f"  -> Success!")
        except Exception as e:
            print(f"  -> Error: {e}")

    print("\n" + "-" * 50)
    print("All tracks preprocessed!")
    print("\nCache files created (*.json)")
    print("Game will load instantly from cache.")

if __name__ == "__main__":
    preprocess_all_tracks()

