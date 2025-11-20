import math


class PhysicsEngine:
    
    def __init__(self):
        self._collision_response = 0.8
    
    def handle_collision(self, vehicle, track):
        corners = vehicle.get_corners()
        
        if track.check_collision(corners):
            # stop and push back
            rad = math.radians(vehicle.angle)
            push_back = 2.0
            
            new_x = vehicle.x - math.cos(rad) * push_back
            new_y = vehicle.y - math.sin(rad) * push_back
            
            vehicle.set_position(new_x, new_y)
            
            # kill most of the speed
            current_speed = vehicle.speed
            vehicle.accelerate(-current_speed * self._collision_response)
            
            return True
        return False
