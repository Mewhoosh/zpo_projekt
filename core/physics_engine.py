import math


class PhysicsEngine:
    
    def __init__(self):
        self._collision_response = 0.8

    def handle_collision(self, vehicle, track):
        corners = vehicle.get_corners()
        
        if track.check_collision(corners):
            rad = math.radians(vehicle.angle)

            push_distance = max(8.0, abs(vehicle.speed) * 1.5)

            new_x = vehicle.x - math.cos(rad) * push_distance
            new_y = vehicle.y - math.sin(rad) * push_distance

            vehicle.set_position(new_x, new_y)

            vehicle.accelerate(-vehicle.speed * 0.9)

            return True
        return False
