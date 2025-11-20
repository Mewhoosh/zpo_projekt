import pygame
from entities.player_car import PlayerCar
from core.track import Track
from core.renderer import Renderer
from core.physics_engine import PhysicsEngine


class GameEngine:
    
    def __init__(self, width=1200, height=800):
        pygame.init()
        self._width = width
        self._height = height
        self._screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Racing Game")
        
        self._clock = pygame.time.Clock()
        self._running = True
        self._fps = 60
        
        self._track = Track(width, height)
        self._renderer = Renderer(self._screen)
        self._physics = PhysicsEngine()
        
        self._player = PlayerCar(100, height // 2)
        self._vehicles = [self._player]
    
    def run(self):
        while self._running:
            dt = self._clock.tick(self._fps) / 1000.0
            
            self._handle_events()
            self._update(dt)
            self._render()
        
        pygame.quit()
    
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._running = False
    
    def _update(self, dt):
        for vehicle in self._vehicles:
            old_x = vehicle.x
            old_y = vehicle.y
            
            vehicle.update(dt)
            
            # check collision and revert if needed
            if self._physics.handle_collision(vehicle, self._track):
                # if still colliding after pushback, revert completely
                if self._track.check_collision(vehicle.get_corners()):
                    vehicle.set_position(old_x, old_y)
    
    def _render(self):
        self._renderer.clear(self._track.background_color)
        self._renderer.draw_track(self._track)
        
        for vehicle in self._vehicles:
            self._renderer.draw_vehicle(vehicle)
        
        speed_text = f"Speed: {abs(self._player.speed):.1f}"
        self._renderer.draw_text(speed_text, 10, 10)
        
        self._renderer.update_display()
