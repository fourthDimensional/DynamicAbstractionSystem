from world.world import Position

import pygame

class DebugRenderObject:
    def __init__(self, position: Position):
        self.position = position

    def tick(self):
        pass

    def render(self, camera, screen):
        if camera.is_in_view(*self.position.get_position()):
            pygame.draw.circle(screen, (255,255,255), camera.world_to_screen(*self.position.get_position()), 15 * camera.zoom)

class FoodObject:
    def __init__(self, position: Position):
        self.decay = 0
        self.position = position

    def tick(self):
        self.decay += 1

        if self.decay > 255:
            self.decay = 0

    def render(self, camera, screen):
        if camera.is_in_view(*self.position.get_position()):
            pygame.draw.circle(screen, (255-self.decay,self.decay,0), camera.world_to_screen(*self.position.get_position()), 5 * camera.zoom)

