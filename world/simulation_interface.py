import pygame


class Camera:
    def __init__(self, screen_width, screen_height, render_buffer=50):
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0
        self.zoom = 1.0
        self.target_zoom = 1.0
        self.smoothing = 0.15  # Higher = more responsive, lower = more smooth
        self.speed = 700
        self.zoom_smoothing = 0.2  # Higher = more responsive, lower = more smooth
        self.is_panning = False
        self.last_mouse_pos = None
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.render_buffer = (
            render_buffer  # Buffer for rendering objects outside the screen
        )

    def update(self, keys, deltatime):
        # Determine movement direction
        dx = 0
        dy = 0
        if keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_s]:
            dy += 1
        if keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_d]:
            dx += 1

        # Normalize direction
        length = (dx ** 2 + dy ** 2) ** 0.5
        if length > 0:
            dx /= length
            dy /= length

        # Apply movement
        self.target_x += dx * self.speed * deltatime / self.zoom
        self.target_y += dy * self.speed * deltatime / self.zoom

        if keys[pygame.K_r]:
            self.target_x = 0
            self.target_y = 0

        # Smooth camera movement with drift
        smoothing_factor = 1 - pow(1 - self.smoothing, deltatime * 60)
        self.x += (self.target_x - self.x) * smoothing_factor
        self.y += (self.target_y - self.y) * smoothing_factor

        # Snap to target if within threshold
        threshold = 0.5
        if abs(self.x - self.target_x) < threshold:
            self.x = self.target_x
        if abs(self.y - self.target_y) < threshold:
            self.y = self.target_y

        # Smooth zoom
        zoom_smoothing_factor = 1 - pow(1 - self.zoom_smoothing, deltatime * 60)
        self.zoom += (self.target_zoom - self.zoom) * zoom_smoothing_factor

        # Snap zoom to target if within threshold
        zoom_threshold = 0.001
        if abs(self.zoom - self.target_zoom) < zoom_threshold:
            self.zoom = self.target_zoom

    def handle_zoom(self, zoom_delta):
        # Zoom in/out with mouse wheel
        zoom_factor = 1.1
        if zoom_delta > 0:  # Zoom in
            self.target_zoom *= zoom_factor
        elif zoom_delta < 0:  # Zoom out
            self.target_zoom /= zoom_factor

        # Clamp zoom levels
        self.target_zoom = max(0.1, min(5.0, self.target_zoom))

    def start_panning(self, mouse_pos):
        self.is_panning = True
        self.last_mouse_pos = mouse_pos

    def stop_panning(self):
        self.is_panning = False
        self.last_mouse_pos = None

    def pan(self, mouse_pos):
        if self.is_panning and self.last_mouse_pos:
            dx = mouse_pos[0] - self.last_mouse_pos[0]
            dy = mouse_pos[1] - self.last_mouse_pos[1]
            self.x -= dx / self.zoom
            self.y -= dy / self.zoom
            self.target_x = self.x  # Sync target position with actual position
            self.target_y = self.y
            self.last_mouse_pos = mouse_pos

    def get_real_coordinates(self, screen_x, screen_y):
        # Convert screen coordinates to world coordinates
        world_x = (screen_x - self.screen_width // 2 + self.x * self.zoom) / self.zoom
        world_y = (screen_y - self.screen_height // 2 + self.y * self.zoom) / self.zoom

        return world_x, world_y

    def is_in_view(self, obj_x, obj_y, margin=0):
        half_w = (self.screen_width + (self.render_buffer * self.zoom)) / (
                2 * self.zoom
        )
        half_h = (self.screen_height + (self.render_buffer * self.zoom)) / (
                2 * self.zoom
        )
        cam_left = self.x - half_w
        cam_right = self.x + half_w
        cam_top = self.y - half_h
        cam_bottom = self.y + half_h
        return (
                cam_left - margin <= obj_x <= cam_right + margin
                and cam_top - margin <= obj_y <= cam_bottom + margin
        )

    def world_to_screen(self, obj_x, obj_y):
        screen_x = (obj_x - self.x) * self.zoom + self.screen_width // 2
        screen_y = (obj_y - self.y) * self.zoom + self.screen_height // 2
        return int(screen_x), int(screen_y)

    def get_relative_size(self, world_size):
        # Converts a world size (e.g., radius or width/height) to screen pixels
        return int(world_size * self.zoom)
