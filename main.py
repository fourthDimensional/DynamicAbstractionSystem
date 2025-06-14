import math

import pygame
import time
import sys
import random

from world.world import World, Position, Rotation
from world.objects import DebugRenderObject, FoodObject, TestVelocityObject, DefaultCell
from world.simulation_interface import Camera

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
GRID_WIDTH = 30  # Number of cells horizontally
GRID_HEIGHT = 25  # Number of cells vertically
CELL_SIZE = 20  # Size of each cell in pixels

DEFAULT_TPS = 20  # Number of ticks per second for the simulation
FOOD_SPAWNING = True


def draw_grid(screen, camera, showing_grid=True):
    # Fill the screen with black
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

    # Fill the grid area awith dark gray background
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

def setup(world: World):
    if FOOD_SPAWNING:
        world.add_object(FoodObject(Position(x=random.randint(-100, 100), y=random.randint(-100, 100))))

    world.add_object(TestVelocityObject(Position(x=random.randint(-100, 100), y=random.randint(-100, 100))))

    world.add_object(DefaultCell(Position(x=0,y=0), Rotation(angle=0)))

    return world


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), vsync=1)
    pygame.display.set_caption("Dynamic Abstraction System Testing")
    clock = pygame.time.Clock()
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, RENDER_BUFFER)

    is_showing_grid = True  # Flag to control grid visibility
    show_interaction_radius = False  # Flag to control interaction radius visibility
    showing_legend = False  # Flag to control legend visibility
    is_paused = False  # Flag to control simulation pause state

    font = pygame.font.Font("freesansbold.ttf", 16)

    tps = DEFAULT_TPS  # Default ticks per second

    last_tick_time = time.perf_counter()  # Tracks the last tick time
    last_tps_time = time.perf_counter()  # Tracks the last TPS calculation time
    tick_counter = 0  # Counts ticks executed
    actual_tps = 0  # Stores the calculated TPS
    total_ticks = 0  # Total ticks executed

    # Selection state
    selecting = False
    select_start = None  # (screen_x, screen_y)
    select_end = None  # (screen_x, screen_y)
    selected_objects = []

    print("Controls:")
    print("WASD - Move camera")
    print("Mouse wheel - Zoom in/out")
    print("Middle mouse button - Pan camera")
    print("R - Reset camera to origin")
    print("ESC or close window - Exit")

    # Initialize world
    world = World(CELL_SIZE, (CELL_SIZE * GRID_WIDTH, CELL_SIZE * GRID_HEIGHT))

    # sets seed to 67 >_<
    random.seed(0)

    world = setup(world)

    running = True
    while running:
        deltatime = clock.get_time() / 1000.0  # Convert milliseconds to seconds
        tick_interval = 1.0 / tps  # Time per tick

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if len(selected_objects) == 0:
                        running = False
                    selecting = False
                    selected_objects = []
                if event.key == pygame.K_g:
                    is_showing_grid = not is_showing_grid
                if event.key == pygame.K_UP:
                    if camera.speed < 2100:
                        camera.speed += 350
                if event.key == pygame.K_DOWN:
                    if camera.speed > 350:
                        camera.speed -= 350
                if event.key == pygame.K_i:
                    show_interaction_radius = not show_interaction_radius
                if event.key == pygame.K_l:
                    showing_legend = not showing_legend
                if event.key == pygame.K_SPACE:
                    is_paused = not is_paused
                if event.key == pygame.K_LSHIFT:
                    tps = DEFAULT_TPS * 4
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LSHIFT:
                    tps = DEFAULT_TPS
            elif event.type == pygame.MOUSEWHEEL:
                camera.handle_zoom(event.y)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 2:  # Middle mouse button
                    camera.start_panning(event.pos)
                elif event.button == 1:  # Left mouse button
                    selecting = True
                    select_start = event.pos
                    select_end = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 2:
                    camera.stop_panning()
                elif event.button == 1 and selecting:
                    selecting = False
                    # Convert screen to world coordinates
                    x1, y1 = camera.get_real_coordinates(*select_start)
                    x2, y2 = camera.get_real_coordinates(*select_end)
                    # If the selection rectangle is very small, treat as a click
                    if (
                            abs(select_start[0] - select_end[0]) < 3
                            and abs(select_start[1] - select_end[1]) < 3
                    ):
                        # Single click: select closest object if in range
                        mouse_world_x, mouse_world_y = camera.get_real_coordinates(
                            *select_start
                        )
                        obj = world.query_closest_object(mouse_world_x, mouse_world_y)
                        selected_objects = []
                        if obj:
                            obj_x, obj_y = obj.position.get_position()
                            # Calculate distance in world coordinates
                            dx = obj_x - mouse_world_x
                            dy = obj_y - mouse_world_y
                            dist = (dx ** 2 + dy ** 2) ** 0.5
                            if dist <= obj.max_visual_width / 2:
                                selected_objects = [obj]
                        print(f"Clicked: selected {len(selected_objects)} object(s)")
                    else:
                        # Drag select: select all in rectangle
                        min_x, max_x = min(x1, x2), max(x1, x2)
                        min_y, max_y = min(y1, y2), max(y1, y2)
                        selected_objects = world.query_objects_in_range(
                            min_x, min_y, max_x, max_y
                        )
                        print(
                            f"Selected {len(selected_objects)} objects in range: {min_x}, {min_y} to {max_x}, {max_y}"
                        )
            elif event.type == pygame.MOUSEMOTION:
                camera.pan(event.pos)
                if selecting:
                    select_end = event.pos

        if not is_paused:
            # Tick logic (runs every tick interval)
            current_time = time.perf_counter()
            while current_time - last_tick_time >= tick_interval:
                last_tick_time += tick_interval
                tick_counter += 1
                total_ticks += 1

                # gets every object in the world and returns amount of FoodObjects
                objects = world.get_objects()
                food = len([obj for obj in objects if isinstance(obj, FoodObject)])


                # ensure selected objects are still valid or have not changed position, if so, reselect them
                selected_objects = [
                    obj for obj in selected_objects if obj in world.get_objects()
                ]

                world.tick_all()

            # Calculate TPS every second
            if current_time - last_tps_time >= 1.0:
                actual_tps = tick_counter
                tick_counter = 0
                last_tps_time += 1.0
        else:
            last_tick_time = time.perf_counter()
            last_tps_time = time.perf_counter()

        # Get pressed keys for smooth movement
        keys = pygame.key.get_pressed()
        camera.update(keys, deltatime)

        # Draw the reference grid
        draw_grid(screen, camera, is_showing_grid)

        # Render everything in the world
        world.render_all(camera, screen)

        if show_interaction_radius:
            for obj in world.get_objects():
                obj_x, obj_y = obj.position.get_position()
                radius = obj.interaction_radius
                if radius > 0 and camera.is_in_view(obj_x, obj_y, margin=radius):
                    if selected_objects and obj not in selected_objects:
                        continue # Skip if not selected and selecting
                    screen_x, screen_y = camera.world_to_screen(obj_x, obj_y)
                    screen_radius = int(radius * camera.zoom)
                    if screen_radius > 0:
                        pygame.draw.circle(
                            screen,
                            (255, 0, 0),  # Red
                            (screen_x, screen_y),
                            screen_radius,
                            1  # 1 pixel thick
                        )

                        # Draw direction arrow
                        rotation_angle = obj.rotation.get_rotation()
                        arrow_length = obj.max_visual_width/2 * camera.zoom  # Scale arrow length with zoom
                        arrow_color = (255, 255, 255)  # Green

                        # Calculate the arrow's end-point based on rotation angle
                        end_x = screen_x + arrow_length * math.cos(math.radians(rotation_angle))
                        end_y = screen_y + arrow_length * math.sin(math.radians(rotation_angle))

                        # Draw the arrow line
                        pygame.draw.line(screen, arrow_color, (screen_x, screen_y), (end_x, end_y), 2)

                        # Draw a rotated triangle for the arrowhead
                        tip_size = 3 * camera.zoom  # Scale triangle tip size with zoom
                        left_tip_x = end_x - tip_size * math.cos(math.radians(rotation_angle + 150 + 180))
                        left_tip_y = end_y - tip_size * math.sin(math.radians(rotation_angle + 150 + 180))
                        right_tip_x = end_x - tip_size * math.cos(math.radians(rotation_angle - 150 + 180))
                        right_tip_y = end_y - tip_size * math.sin(math.radians(rotation_angle - 150 + 180))

                        # Draw arrowhead (triangle) for direction
                        pygame.draw.polygon(
                            screen,
                            arrow_color,
                            [(end_x, end_y), (left_tip_x, left_tip_y), (right_tip_x, right_tip_y)]
                        )

                        # Draw angular acceleration arrow (if present)
                        if hasattr(obj, 'angular_acceleration'):
                            angular_acceleration = obj.angular_acceleration

                            # Scale the angular acceleration value for visibility
                            angular_accel_magnitude = abs(
                                angular_acceleration) * 50 * camera.zoom  # Use absolute magnitude for scaling

                            # Determine the perpendicular direction based on the sign of angular_acceleration
                            angular_direction = rotation_angle + 90 if angular_acceleration >= 0 else rotation_angle - 90

                            # Calculate the end of the angular acceleration vector
                            angular_acc_end_x = end_x + angular_accel_magnitude * math.cos(
                                math.radians(angular_direction))
                            angular_acc_end_y = end_y + angular_accel_magnitude * math.sin(
                                math.radians(angular_direction))

                            # Draw the angular acceleration vector as a red line
                            pygame.draw.line(screen, (52, 134, 235), (end_x, end_y),
                                             (angular_acc_end_x, angular_acc_end_y), 2)

                            # Add an arrowhead to the angular acceleration vector
                            angular_tip_size = 2.5 * camera.zoom
                            left_angular_tip_x = angular_acc_end_x - angular_tip_size * math.cos(
                                math.radians(angular_direction + 150 + 180))
                            left_angular_tip_y = angular_acc_end_y - angular_tip_size * math.sin(
                                math.radians(angular_direction + 150 + 180))
                            right_angular_tip_x = angular_acc_end_x - angular_tip_size * math.cos(
                                math.radians(angular_direction - 150 + 180))
                            right_angular_tip_y = angular_acc_end_y - angular_tip_size * math.sin(
                                math.radians(angular_direction - 150 + 180))

                            # Draw arrowhead (triangle) for angular acceleration
                            pygame.draw.polygon(
                                screen,
                                (52, 134, 235),  # Red arrowhead
                                [(angular_acc_end_x, angular_acc_end_y), (left_angular_tip_x, left_angular_tip_y),
                                 (right_angular_tip_x, right_angular_tip_y)]
                            )

                        # If object has an acceleration attribute, draw a red vector with arrowhead
                        if hasattr(obj, 'acceleration') and isinstance(obj.acceleration, tuple) and len(
                                obj.acceleration) == 2:
                            acc_x, acc_y = obj.acceleration

                            # Calculate acceleration magnitude and direction
                            acc_magnitude = math.sqrt(acc_x ** 2 + acc_y ** 2)
                            if acc_magnitude > 0:
                                acc_direction = math.degrees(math.atan2(acc_y, acc_x))  # Get the angle in degrees

                                # Calculate scaled acceleration vector's end point
                                acc_vector_length = acc_magnitude * 1000 * camera.zoom  # Scale length with zoom
                                acc_end_x = screen_x + acc_vector_length * math.cos(math.radians(acc_direction))
                                acc_end_y = screen_y + acc_vector_length * math.sin(math.radians(acc_direction))

                                # Draw the acceleration vector as a red line
                                pygame.draw.line(screen, (255, 0, 0), (screen_x, screen_y), (acc_end_x, acc_end_y), 2)

                                # Add arrowhead to acceleration vector
                                acc_tip_size = 5 * camera.zoom
                                left_tip_x = acc_end_x - acc_tip_size * math.cos(math.radians(acc_direction + 150 + 180))
                                left_tip_y = acc_end_y - acc_tip_size * math.sin(math.radians(acc_direction + 150 + 180))
                                right_tip_x = acc_end_x - acc_tip_size * math.cos(math.radians(acc_direction - 150 + 180))
                                right_tip_y = acc_end_y - acc_tip_size * math.sin(math.radians(acc_direction - 150 + 180))

                                pygame.draw.polygon(
                                    screen,
                                    (255, 0, 0),  # Red arrowhead
                                    [(acc_end_x, acc_end_y), (left_tip_x, left_tip_y), (right_tip_x, right_tip_y)]
                                )

                        # If object has a velocity attribute, draw a blue vector with arrowhead
                        if hasattr(obj, 'velocity') and isinstance(obj.velocity, tuple) and len(obj.velocity) == 2:
                            vel_x, vel_y = obj.velocity

                            # Calculate velocity magnitude and direction
                            vel_magnitude = math.sqrt(vel_x ** 2 + vel_y ** 2)
                            if vel_magnitude > 0:
                                vel_direction = math.degrees(math.atan2(vel_y, vel_x))  # Get the angle in degrees

                                # Calculate scaled velocity vector's end point
                                vel_vector_length = vel_magnitude * 50 * camera.zoom  # Scale length with zoom
                                vel_end_x = screen_x + vel_vector_length * math.cos(math.radians(vel_direction))
                                vel_end_y = screen_y + vel_vector_length * math.sin(math.radians(vel_direction))

                                # Draw the velocity vector as a blue line
                                pygame.draw.line(screen, (0, 0, 255), (screen_x, screen_y), (vel_end_x, vel_end_y), 2)

                                # Add arrowhead to velocity vector
                                vel_tip_size = 5 * camera.zoom
                                left_tip_x = vel_end_x - vel_tip_size * math.cos(math.radians(vel_direction + 150 + 180))
                                left_tip_y = vel_end_y - vel_tip_size * math.sin(math.radians(vel_direction + 150 + 180))
                                right_tip_x = vel_end_x - vel_tip_size * math.cos(math.radians(vel_direction - 150 + 180))
                                right_tip_y = vel_end_y - vel_tip_size * math.sin(math.radians(vel_direction - 150 + 180))

                                pygame.draw.polygon(
                                    screen,
                                    (0, 0, 255),  # Blue arrowhead
                                    [(vel_end_x, vel_end_y), (left_tip_x, left_tip_y), (right_tip_x, right_tip_y)]
                                )

        # Draw selection rectangle if selecting
        if selecting and select_start and select_end:
            rect_color = (128, 128, 128, 80)  # Gray, semi-transparent
            border_color = (80, 80, 90)  # Slightly darker gray for border

            left = min(select_start[0], select_end[0])
            top = min(select_start[1], select_end[1])
            width = abs(select_end[0] - select_start[0])
            height = abs(select_end[1] - select_start[1])

            s = pygame.Surface((width, height), pygame.SRCALPHA)
            s.fill(rect_color)
            screen.blit(s, (left, top))

            # Draw 1-pixel border
            pygame.draw.rect(
                screen, border_color, pygame.Rect(left, top, width, height), 1
            )

        # Draw blue outline for selected objects
        for obj in selected_objects:
            obj_x, obj_y = obj.position.get_position()
            width = obj.max_visual_width if hasattr(obj, "max_visual_width") else 10
            screen_x, screen_y = camera.world_to_screen(obj_x, obj_y)
            size = camera.get_relative_size(width)
            rect = pygame.Rect(screen_x - size // 2, screen_y - size // 2, size, size)
            pygame.draw.rect(screen, (0, 128, 255), rect, 1)  # Blue, 1px wide

        # Render mouse position as text in top left of screen
        mouse_x, mouse_y = camera.get_real_coordinates(*pygame.mouse.get_pos())
        mouse_text = font.render(f"Mouse: ({mouse_x:.2f}, {mouse_y:.2f})", True, WHITE)
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

        # Render tick count in bottom left
        tick_text = font.render(f"Ticks: {total_ticks}", True, WHITE)
        tick_rect = tick_text.get_rect()
        tick_rect.bottomleft = (10, SCREEN_HEIGHT - 10)
        screen.blit(tick_text, tick_rect)

        if len(selected_objects) >= 1:
            i = 0
            max_width = SCREEN_WIDTH - 20  # Leave some padding from the right edge
            for each in selected_objects:
                obj = each
                text = f"Object: {str(obj)}"
                words = text.split()  # Split text into words
                line = ""
                line_height = 20  # Height of each line of text
                line_offset = 0

                for word in words:
                    test_line = f"{line} {word}".strip()
                    test_width, _ = font.size(test_line)

                    # Check if the line width exceeds the limit
                    if test_width > max_width and line:
                        obj_text = font.render(line, True, WHITE)
                        obj_rect = obj_text.get_rect()
                        obj_rect.topleft = (10, 30 + i * line_height + line_offset)
                        screen.blit(obj_text, obj_rect)
                        line = word  # Start a new line
                        line_offset += line_height
                    else:
                        line = test_line

                # Render the last line
                if line:
                    obj_text = font.render(line, True, WHITE)
                    obj_rect = obj_text.get_rect()
                    obj_rect.topleft = (10, 30 + i * line_height + line_offset)
                    screen.blit(obj_text, obj_rect)

                i += 1

        legend_font = pygame.font.Font("freesansbold.ttf", 14)

        keymap_legend = [
            ("WASD", "Move camera"),
            ("Mouse wheel", "Zoom in/out"),
            ("Middle mouse", "Pan camera"),
            ("R", "Reset camera"),
            ("G", "Toggle grid"),
            ("I", "Toggle interaction radius"),
            ("ESC", "Deselect/Exit"),
            ("Left click", "Select object(s)"),
            ("Drag select", "Select multiple objects"),
            ("Click on object", "Select closest object in range"),
            ("Up/Down", "Increase/Decrease camera speed"),
            ("Shift", "Double TPS (for testing)"),
            ("L", "Toggle this legend"),
            ("Space", "Pause/Resume simulation"),
        ]

        if showing_legend:
            # Split into two columns
            mid = (len(keymap_legend) + 1) // 2
            left_col = keymap_legend[:mid]
            right_col = keymap_legend[mid:]

            legend_font_height = legend_font.get_height()
            column_gap = 40  # Space between columns

            # Calculate max width for each column
            left_width = max(legend_font.size(f"{k}: {v}")[0] for k, v in left_col)
            right_width = max(legend_font.size(f"{k}: {v}")[0] for k, v in right_col)
            legend_width = left_width + right_width + column_gap
            legend_height = max(len(left_col), len(right_col)) * legend_font_height + 10

            legend_x = (SCREEN_WIDTH - legend_width) // 2
            legend_y = SCREEN_HEIGHT - legend_height - 10

            # Draw left column
            for i, (key, desc) in enumerate(left_col):
                text = legend_font.render(f"{key}: {desc}", True, WHITE)
                text_rect = text.get_rect()
                text_rect.left = legend_x
                text_rect.top = legend_y + 5 + i * legend_font_height
                screen.blit(text, text_rect)

            # Draw right column
            for i, (key, desc) in enumerate(right_col):
                text = legend_font.render(f"{key}: {desc}", True, WHITE)
                text_rect = text.get_rect()
                text_rect.left = legend_x + left_width + column_gap
                text_rect.top = legend_y + 5 + i * legend_font_height
                screen.blit(text, text_rect)
        else:
            # just show l to toggle legend
            legend_text = legend_font.render("Press 'L' to show controls", True, WHITE)
            legend_rect = legend_text.get_rect()
            legend_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20)
            screen.blit(legend_text, legend_rect)

        if is_paused:
            pause_text = font.render("Press 'Space' to unpause", True, WHITE)
            pause_rect = pause_text.get_rect()
            pause_rect.center = (SCREEN_WIDTH // 2, 20)
            screen.blit(pause_text, pause_rect)

        # Update display
        pygame.display.flip()
        clock.tick(180)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
