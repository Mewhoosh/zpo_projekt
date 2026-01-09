from PIL import Image
import numpy as np
import json
import os


class TrackLoader:

    def __init__(self):
        self.wall_color = (0, 0, 0)
        self.road_color = (255, 255, 255)
        self.start_color = (255, 0, 0)
        self.checkpoint_color = (0, 255, 0)

    def load_from_png(self, filepath):
        """
        Load track from PNG. First checks if cached JSON exists.
        If not, processes PNG and creates cache.
        """
        cache_file = filepath.replace('.png', '_cache.json')

        # Try to load from cache first
        if os.path.exists(cache_file):
            png_time = os.path.getmtime(filepath)
            cache_time = os.path.getmtime(cache_file)

            # Use cache if it's newer than PNG
            if cache_time >= png_time:
                with open(cache_file, 'r') as f:
                    return json.load(f)

        # No cache or outdated - process PNG
        print(f"Processing {filepath}...")
        track_data = self._process_png(filepath)

        # Save to cache
        with open(cache_file, 'w') as f:
            json.dump(track_data, f)
        print(f"Cached to {cache_file}")

        return track_data

    def _process_png(self, filepath):
        """Process PNG file completely - all pixels."""
        img = Image.open(filepath).convert('RGB')
        width, height = img.size
        pixels = np.array(img)

        walls = []
        checkpoints = []
        start_position = (100, height // 2)
        start_finish_line = None

        # Find yellow start/finish line
        yellow_pixels = []
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[y, x]
                if abs(r - 255) < 30 and abs(g - 255) < 30 and b < 50:
                    yellow_pixels.append((x, y))

        if yellow_pixels:
            avg_x = sum(p[0] for p in yellow_pixels) // len(yellow_pixels)
            avg_y = sum(p[1] for p in yellow_pixels) // len(yellow_pixels)
            start_position = (avg_x, avg_y)
            x1, y1 = yellow_pixels[0]
            x2, y2 = yellow_pixels[-1]
            start_finish_line = {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2}

        # Extract walls - group adjacent black pixels
        visited = np.zeros((height, width), dtype=bool)

        for y in range(height):
            for x in range(width):
                if visited[y, x]:
                    continue

                r, g, b = pixels[y, x]

                if r < 50 and g < 50 and b < 50:
                    # Found wall pixel, create rectangle
                    wall_rect = self._extract_wall_rect(pixels, visited, x, y, width, height)
                    if wall_rect:
                        walls.append(wall_rect)

        # Extract checkpoints from green pixels
        checkpoints = self._extract_checkpoints(pixels, width, height)

        return {
            'walls': walls,
            'checkpoints': checkpoints,
            'start_position': start_position,
            'start_finish_line': start_finish_line,
            'width': width,
            'height': height
        }

    def _extract_wall_rect(self, pixels, visited, start_x, start_y, width, height):
        """Extract rectangular wall from starting position."""
        # Find max width
        rect_width = 0
        for x in range(start_x, width):
            r, g, b = pixels[start_y, x]
            if r < 50 and g < 50 and b < 50 and not visited[start_y, x]:
                rect_width += 1
            else:
                break

        if rect_width == 0:
            return None

        # Find max height
        rect_height = 0
        for y in range(start_y, height):
            valid = True
            for x in range(start_x, start_x + rect_width):
                if x >= width:
                    valid = False
                    break
                r, g, b = pixels[y, x]
                if not (r < 50 and g < 50 and b < 50) or visited[y, x]:
                    valid = False
                    break

            if valid:
                rect_height += 1
            else:
                break

        if rect_height == 0:
            return None

        # Mark as visited
        for y in range(start_y, start_y + rect_height):
            for x in range(start_x, start_x + rect_width):
                if y < height and x < width:
                    visited[y, x] = True

        return {
            'x': start_x,
            'y': start_y,
            'width': rect_width,
            'height': rect_height
        }

    def _extract_checkpoints(self, pixels, width, height):
        """Extract checkpoint lines from green pixels."""
        checkpoints = []
        visited = np.zeros((height, width), dtype=bool)
        checkpoint_id = 0

        for y in range(height):
            for x in range(width):
                if visited[y, x]:
                    continue

                r, g, b = pixels[y, x]

                if g > 200 and r < 100 and b < 100:
                    # Found green pixel, trace the line
                    line = self._trace_checkpoint_line(pixels, visited, x, y, width, height)
                    if line and len(line) > 3:
                        x1, y1 = line[0]
                        x2, y2 = line[-1]
                        checkpoints.append({
                            'x1': x1, 'y1': y1,
                            'x2': x2, 'y2': y2,
                            'id': checkpoint_id,
                            'passed': False
                        })
                        checkpoint_id += 1

        return checkpoints

    def _trace_checkpoint_line(self, pixels, visited, start_x, start_y, width, height):
        """Trace a line of green pixels."""
        line = [(start_x, start_y)]
        visited[start_y, start_x] = True

        directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]
        current_x, current_y = start_x, start_y

        for _ in range(max(width, height)):
            found_next = False

            for dx, dy in directions:
                next_x = current_x + dx
                next_y = current_y + dy

                if 0 <= next_x < width and 0 <= next_y < height:
                    if not visited[next_y, next_x]:
                        r, g, b = pixels[next_y, next_x]
                        if g > 200 and r < 100 and b < 100:
                            line.append((next_x, next_y))
                            visited[next_y, next_x] = True
                            current_x, current_y = next_x, next_y
                            found_next = True
                            break

            if not found_next:
                break

        return line




