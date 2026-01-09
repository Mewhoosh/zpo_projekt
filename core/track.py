class Track:

    def __init__(self, width=None, height=None, track_data=None):
        """
        Initialize track either from dimensions (creates default track)
        or from track_data dict (loaded from PNG).

        Args:
            width: Track width (for default track)
            height: Track height (for default track)
            track_data: Dict with walls, checkpoints, start_position, width, height (from TrackLoader)
        """
        if track_data:
            self._width = track_data['width']
            self._height = track_data['height']
            self._walls = track_data['walls']
            self._checkpoints = track_data['checkpoints']
            self._start_position = track_data['start_position']
            self._start_finish_line = track_data.get('start_finish_line', None)
        else:
            self._width = width or 1200
            self._height = height or 800
            self._walls = []
            self._checkpoints = []
            self._start_position = (100, height // 2 if height else 400)
            self._start_finish_line = None
            self._setup_basic_track()
            self._setup_checkpoints()

        self._background_color = (50, 50, 50)
        self._wall_color = (100, 100, 100)
        self._checkpoint_color = (255, 215, 0)

    def _setup_basic_track(self):
        wall_thickness = 20

        # outer walls
        self._walls.append({
            'x': 0, 'y': 0,
            'width': self._width, 'height': wall_thickness
        })
        self._walls.append({
            'x': 0, 'y': self._height - wall_thickness,
            'width': self._width, 'height': wall_thickness
        })
        self._walls.append({
            'x': 0, 'y': 0,
            'width': wall_thickness, 'height': self._height
        })
        self._walls.append({
            'x': self._width - wall_thickness, 'y': 0,
            'width': wall_thickness, 'height': self._height
        })

        # inner obstacle
        self._walls.append({
            'x': self._width // 2 - 100, 'y': self._height // 2 - 50,
            'width': 200, 'height': 100
        })

    def _setup_checkpoints(self):
        margin = 50
        # Right side checkpoint
        self._checkpoints.append({
            'x1': self._width - 200, 'y1': margin,
            'x2': self._width - 200, 'y2': self._height - margin,
            'id': 0,
            'passed': False
        })

        # Top checkpoint
        self._checkpoints.append({
            'x1': self._width - margin, 'y1': 150,
            'x2': margin, 'y2': 150,
            'id': 1,
            'passed': False
        })

        # Left side checkpoint
        self._checkpoints.append({
            'x1': 200, 'y1': margin,
            'x2': 200, 'y2': self._height - margin,
            'id': 2,
            'passed': False
        })

        # Bottom checkpoint (finish line)
        self._checkpoints.append({
            'x1': self._width - margin, 'y1': self._height - 150,
            'x2': margin, 'y2': self._height - 150,
            'id': 3,
            'passed': False
        })

    def check_checkpoint_crossing(self, prev_x, prev_y, curr_x, curr_y, next_checkpoint_id):
        if next_checkpoint_id >= len(self._checkpoints):
            return False

        checkpoint = self._checkpoints[next_checkpoint_id]

        # Line intersection algorithm
        def ccw(ax, ay, bx, by, cx, cy):
            return (cy - ay) * (bx - ax) > (by - ay) * (cx - ax)

        x1, y1 = checkpoint['x1'], checkpoint['y1']
        x2, y2 = checkpoint['x2'], checkpoint['y2']

        a = ccw(x1, y1, curr_x, curr_y, prev_x, prev_y)
        b = ccw(x2, y2, curr_x, curr_y, prev_x, prev_y)
        c = ccw(x1, y1, x2, y2, curr_x, curr_y)
        d = ccw(x1, y1, x2, y2, prev_x, prev_y)

        return (a != b) and (c != d)

    def reset_checkpoints(self):
        for checkpoint in self._checkpoints:
            checkpoint['passed'] = False

    @property
    def walls(self):
        return self._walls

    @property
    def checkpoints(self):
        return self._checkpoints

    @property
    def start_position(self):
        return self._start_position

    @property
    def start_finish_line(self):
        return self._start_finish_line

    @property
    def total_checkpoints(self):
        return len(self._checkpoints)

    @property
    def background_color(self):
        return self._background_color

    @property
    def wall_color(self):
        return self._wall_color

    @property
    def checkpoint_color(self):
        return self._checkpoint_color

    def check_collision(self, corners):
        for corner_x, corner_y in corners:
            for wall in self._walls:
                if (wall['x'] <= corner_x <= wall['x'] + wall['width'] and
                    wall['y'] <= corner_y <= wall['y'] + wall['height']):
                    return True
        return False

