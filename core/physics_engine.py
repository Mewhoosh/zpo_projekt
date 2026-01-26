import math


class PhysicsEngine:
    
    def __init__(self):
        self._collision_response = 0.8

    def handle_collision(self, vehicle, track):
        corners = vehicle.get_corners()
        
        if track.check_collision(corners):
            # Znajdź które rogi są w kolizji i oblicz wektor odpychania
            push_x, push_y = self._calculate_push_vector(corners, track)

            if push_x == 0 and push_y == 0:
                # Fallback - odpychaj wstecz
                rad = math.radians(vehicle.angle)
                push_x = -math.cos(rad) * 10
                push_y = -math.sin(rad) * 10

            new_x = vehicle.x + push_x
            new_y = vehicle.y + push_y

            vehicle.set_position(new_x, new_y)
            vehicle.accelerate(-vehicle.speed)  # Pełne zatrzymanie przy kolizji

            return True
        return False

    def _calculate_push_vector(self, corners, track):
        """Oblicz wektor odpychania na podstawie kolizji rogów ze ścianami."""
        total_push_x = 0.0
        total_push_y = 0.0
        collision_count = 0

        for corner_x, corner_y in corners:
            for wall in track.walls:
                wx, wy = wall['x'], wall['y']
                ww, wh = wall['width'], wall['height']

                if wx <= corner_x <= wx + ww and wy <= corner_y <= wy + wh:
                    # Róg jest w ścianie - oblicz kierunek wyjścia
                    # Znajdź najbliższą krawędź ściany
                    dist_left = corner_x - wx
                    dist_right = (wx + ww) - corner_x
                    dist_top = corner_y - wy
                    dist_bottom = (wy + wh) - corner_y

                    min_dist = min(dist_left, dist_right, dist_top, dist_bottom)
                    push_amount = min_dist + 2  # Minimalny margines żeby wyjść ze ściany

                    if min_dist == dist_left:
                        total_push_x -= push_amount
                    elif min_dist == dist_right:
                        total_push_x += push_amount
                    elif min_dist == dist_top:
                        total_push_y -= push_amount
                    else:
                        total_push_y += push_amount

                    collision_count += 1

        if collision_count > 0:
            return total_push_x / collision_count, total_push_y / collision_count
        return 0, 0

