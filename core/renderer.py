import pygame


class Renderer:
    
    def __init__(self, screen):
        self._screen = screen
        self._font = pygame.font.Font(None, 36)
    
    def clear(self, color):
        self._screen.fill(color)
    
    def draw_track(self, track, show_checkpoints=False):
        for wall in track.walls:
            pygame.draw.rect(
                self._screen, 
                track.wall_color,
                (wall['x'], wall['y'], wall['width'], wall['height'])
            )

        if track.start_finish_line:
            pygame.draw.line(
                self._screen,
                (255, 255, 0),
                (track.start_finish_line['x1'], track.start_finish_line['y1']),
                (track.start_finish_line['x2'], track.start_finish_line['y2']),
                5
            )

        if show_checkpoints:
            for checkpoint in track.checkpoints:
                pygame.draw.line(
                    self._screen,
                    track.checkpoint_color,
                    (checkpoint['x1'], checkpoint['y1']),
                    (checkpoint['x2'], checkpoint['y2']),
                    5
                )

    def draw_vehicle(self, vehicle):
        corners = vehicle.get_corners()
        # Draw main body
        pygame.draw.polygon(self._screen, vehicle.color, corners)
        # Draw front indicator (red line on front)
        pygame.draw.line(self._screen, (255, 0, 0), corners[1], corners[2], 3)

    def draw_text(self, text, x, y, color=(255, 255, 255)):
        surface = self._font.render(text, True, color)
        self._screen.blit(surface, (x, y))
    
    def update_display(self):
        pygame.display.flip()
