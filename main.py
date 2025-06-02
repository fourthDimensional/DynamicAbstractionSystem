import pygame
import time
import sys

from world.world import World, Position
from world.render_objects import DebugRenderObject, FoodObject

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1920 / 2
SCREEN_HEIGHT = 1080 / 2
BLACK = (0, 0, 0)
DARK_GRAY = (64, 64, 64)
GRAY = (128, 128, 128)
WHITE = (255, 255, 255)
RENDER_BUFFER = 50
SPEED = 700 # Pixels per second

# Grid settings
GRID_WIDTH = 20  # Number of cells horizontally
GRID_HEIGHT = 15  # Number of cells vertically
CELL_SIZE = 20  # Size of each cell in pixels

DEFAULT_TPS = 200  # Amount of ticks per second for the simulation


class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0
        self.zoom = 1.0
        self.target_zoom = 1.0
        self.smoothing = 0.15  # Higher = more responsive, lower = more smooth
        self.speed = SPEED
        self.zoom_smoothing = 0.10
        self.is_panning = False
        self.last_mouse_pos = None

    def update(self, keys, deltatime):
        # Update target position based on input
        if keys[pygame.K_w]:
            self.target_y -= self.speed * deltatime / self.zoom
        if keys[pygame.K_s]:
            self.target_y += self.speed * deltatime / self.zoom
        if keys[pygame.K_a]:
            self.target_x -= self.speed * deltatime / self.zoom
        if keys[pygame.K_d]:
            self.target_x += self.speed * deltatime / self.zoom
        if keys[pygame.K_r]:
            self.target_x = 0
            self.target_y = 0

        # Smooth camera movement with drift
        smoothing_factor = 1 - pow(
            1 - self.smoothing, deltatime * 60
        )  # Adjust smoothing based on deltatime
        self.x += (self.target_x - self.x) * smoothing_factor
        self.y += (self.target_y - self.y) * smoothing_factor

        # Smooth zoom
        zoom_smoothing_factor = 1 - pow(1 - self.zoom_smoothing, deltatime * 60)
        self.zoom += (self.target_zoom - self.zoom) * zoom_smoothing_factor

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
        world_x = (screen_x - SCREEN_WIDTH // 2 + self.x * self.zoom) / self.zoom
        world_y = (screen_y - SCREEN_HEIGHT // 2 + self.y * self.zoom) / self.zoom

        return world_x, world_y

    def is_in_view(self, obj_x, obj_y, margin=0):
        half_w = (SCREEN_WIDTH + (RENDER_BUFFER * self.zoom)) / (2 * self.zoom)
        half_h = (SCREEN_HEIGHT + (RENDER_BUFFER * self.zoom)) / (2 * self.zoom)
        cam_left = self.x - half_w
        cam_right = self.x + half_w
        cam_top = self.y - half_h
        cam_bottom = self.y + half_h
        return (cam_left - margin <= obj_x <= cam_right + margin and
                cam_top - margin <= obj_y <= cam_bottom + margin)

    def world_to_screen(self, obj_x, obj_y):
        screen_x = (obj_x - self.x) * self.zoom + SCREEN_WIDTH // 2
        screen_y = (obj_y - self.y) * self.zoom + SCREEN_HEIGHT // 2
        return int(screen_x), int(screen_y)

    def get_relative_size(self, world_size):
        # Converts a world size (e.g., radius or width/height) to screen pixels
        return int(world_size * self.zoom)


def draw_grid(screen, camera, showing_grid=True):
    # Fill screen with black
    screen.fill(BLACK)

    # Calculate effective cell size with zoom
    effective_cell_size = CELL_SIZE * camera.zoom

    # Calculate grid boundaries in world coordinates (centered at 0,0)
    grid_world_width = GRID_WIDTH * effective_cell_size
    grid_world_height = GRID_HEIGHT * effective_cell_size

    # Calculate grid position relative to camera (with grid centered at 0,0)
    grid_center_x = SCREEN_WIDTH // 2 - camera.x * camera.zoom
    grid_center_y = SCREEN_HEIGHT // 2 - camera.y * camera.zoom

    grid_left = grid_center_x - grid_world_width // 2
    grid_top = grid_center_y - grid_world_height // 2
    grid_right = grid_left + grid_world_width
    grid_bottom = grid_top + grid_world_height

    # Check if grid should be shown
    if not showing_grid:
        return  # Exit early if grid is not visible

    # Check if grid is visible on screen
    if (
            grid_right < 0
            or grid_left > SCREEN_WIDTH
            or grid_bottom < 0
            or grid_top > SCREEN_HEIGHT
    ):
        return  # Grid is completely off-screen

    # Fill the grid area with dark gray background
    grid_rect = pygame.Rect(
        max(0, grid_left),
        max(0, grid_top),
        min(SCREEN_WIDTH, grid_right) - max(0, grid_left),
        min(SCREEN_HEIGHT, grid_bottom) - max(0, grid_top),
    )

    # Only draw if the rectangle has positive dimensions
    if grid_rect.width > 0 and grid_rect.height > 0:
        pygame.draw.rect(screen, DARK_GRAY, grid_rect)

    # Draw vertical grid lines (only if zoom is high enough to see them clearly)
    if effective_cell_size > 4:
        # Precompute grid boundaries
        vertical_lines = []
        horizontal_lines = []

        for i in range(max(GRID_WIDTH, GRID_HEIGHT) + 1):
            # Vertical lines
            if i <= GRID_WIDTH:
                line_x = grid_left + i * effective_cell_size
                if 0 <= line_x <= SCREEN_WIDTH:
                    start_y = max(0, grid_top)
                    end_y = min(SCREEN_HEIGHT, grid_bottom)
                    if start_y < end_y:
                        vertical_lines.append(((line_x, start_y), (line_x, end_y)))

            # Horizontal lines
            if i <= GRID_HEIGHT:
                line_y = grid_top + i * effective_cell_size
                if 0 <= line_y <= SCREEN_HEIGHT:
                    start_x = max(0, grid_left)
                    end_x = min(SCREEN_WIDTH, grid_right)
                    if start_x < end_x:
                        horizontal_lines.append(((start_x, line_y), (end_x, line_y)))

        # Draw all vertical lines in one batch
        for start, end in vertical_lines:
            pygame.draw.line(screen, GRAY, start, end)

        # Draw all horizontal lines in one batch
        for start, end in horizontal_lines:
            pygame.draw.line(screen, GRAY, start, end)

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), vsync=1)
    pygame.display.set_caption("Dynamic Abstraction System Testing")
    clock = pygame.time.Clock()
    camera = Camera()

    is_showing_grid = True  # Flag to control grid visibility

    font = pygame.font.Font("freesansbold.ttf", 16)

    tick_interval = 1.0 / DEFAULT_TPS  # Time per tick
    last_tick_time = time.perf_counter()  # Tracks the last tick time
    last_tps_time = time.perf_counter()  # Tracks the last TPS calculation time
    tick_counter = 0  # Counts ticks executed
    actual_tps = 0  # Stores the calculated TPS

    print("Controls:")
    print("WASD - Move camera")
    print("Mouse wheel - Zoom in/out")
    print("Middle mouse button - Pan camera")
    print("R - Reset camera to origin")
    print("ESC or close window - Exit")

    # Initialize world
    world = World()

    world.add_object(DebugRenderObject(Position(0,0)))
    world.add_object(FoodObject(Position(100, 0)))

    running = True
    while running:
        deltatime = clock.get_time() / 1000.0  # Convert milliseconds to seconds

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_g:
                    is_showing_grid = not is_showing_grid
                if event.key == pygame.K_UP:
                    if camera.speed < 2100:
                        camera.speed += 350
                if event.key == pygame.K_DOWN:
                    if camera.speed > 350:
                        camera.speed -= 350
            elif event.type == pygame.MOUSEWHEEL:
                camera.handle_zoom(event.y)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 2:  # Middle mouse button
                    camera.start_panning(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 2:  # Middle mouse button
                    camera.stop_panning()
            elif event.type == pygame.MOUSEMOTION:
                camera.pan(event.pos)

        # Get pressed keys for smooth movement
        keys = pygame.key.get_pressed()
        camera.update(keys, deltatime)

        # Tick logic (runs every tick interval)
        current_time = time.perf_counter()
        while current_time - last_tick_time >= tick_interval:
            last_tick_time += tick_interval
            tick_counter += 1
            # Add your tick-specific logic here
            print("Tick logic executed")
            world.tick_all()

        # Calculate TPS every second
        if current_time - last_tps_time >= 1.0:
            actual_tps = tick_counter
            tick_counter = 0
            last_tps_time += 1.0

        # Draw the reference grid
        draw_grid(screen, camera, is_showing_grid)

        # Render everything in the world
        world.render_all(camera, screen)


        # Render mouse position as text in top left of screen
        mouse_x, mouse_y = camera.get_real_coordinates(*pygame.mouse.get_pos())
        mouse_text = font.render(f"Mouse: ({mouse_x}, {mouse_y})", True, WHITE)
        text_rect = mouse_text.get_rect()
        text_rect.topleft = (10, 10)
        screen.blit(mouse_text, text_rect)

        # Render FPS in top right
        fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, WHITE)
        fps_rect = fps_text.get_rect()
        fps_rect.topright = (SCREEN_WIDTH - 10, 10)
        screen.blit(fps_text, fps_rect)

        # Render TPS in bottom right
        tps_text = font.render(f"TPS: {actual_tps}", True, WHITE)
        tps_rect = tps_text.get_rect()
        tps_rect.bottomright = (SCREEN_WIDTH - 10, SCREEN_HEIGHT - 10)
        screen.blit(tps_text, tps_rect)

        # Update display
        pygame.display.flip()
        clock.tick(180)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
