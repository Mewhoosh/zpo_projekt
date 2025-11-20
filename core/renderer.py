import pygame


class Renderer:
    
    def __init__(self, screen):
        self._screen = screen
        self._font = pygame.font.Font(None, 36)
    
    def clear(self, color):
        self._screen.fill(color)
    
    def draw_track(self, track):
        for wall in track.walls:
            pygame.draw.rect(
                self._screen, 
                track.wall_color,
                (wall['x'], wall['y'], wall['width'], wall['height'])
            )
    
    def draw_vehicle(self, vehicle):
        corners = vehicle.get_corners()
        pygame.draw.polygon(self._screen, vehicle.color, corners)
    
    def draw_text(self, text, x, y, color=(255, 255, 255)):
        surface = self._font.render(text, True, color)
        self._screen.blit(surface, (x, y))
    
    def update_display(self):
        pygame.display.flip()
