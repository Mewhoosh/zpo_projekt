class Track:
    
    def __init__(self, width, height):
        self._width = width
        self._height = height
        self._walls = []
        self._background_color = (50, 50, 50)
        self._wall_color = (100, 100, 100)
        self._setup_basic_track()
    
    def _setup_basic_track(self):
        margin = 50
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
    
    @property
    def walls(self):
        return self._walls
    
    @property
    def background_color(self):
        return self._background_color
    
    @property
    def wall_color(self):
        return self._wall_color
    
    def check_collision(self, corners):
        for corner_x, corner_y in corners:
            for wall in self._walls:
                if (wall['x'] <= corner_x <= wall['x'] + wall['width'] and
                    wall['y'] <= corner_y <= wall['y'] + wall['height']):
                    return True
        return False
