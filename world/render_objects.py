from world.world import Position, BaseEntity
import pygame

# returns desired yellow value for food decay
def food_decay_yellow(decay):
    if decay < 128:
        return decay
    else:
        return 255 - decay

class DebugRenderObject(BaseEntity):
    def __init__(self, position: Position, radius=5):
        super().__init__(position)

        self.neighbors = 0
        self.radius = radius
        self.max_visual_width = radius * 2
        self.interaction_radius = 50
        self.flags = {
            "death": False,
            "can_interact": True,
        }

    def tick(self, interactable=None):
        if interactable is None:
            interactable = []
        self.neighbors = len(interactable)

        return self

    def render(self, camera, screen):
        if camera.is_in_view(*self.position.get_position()):
            pygame.draw.circle(
                screen,
                (50, 50, min([255, (self.neighbors + 4) * 30])),
                camera.world_to_screen(*self.position.get_position()),
                self.radius * camera.zoom,
            )

    def __repr__(self):
        return f"DebugRenderObject({self.position}, neighbors={self.neighbors})"
class FoodObject:
    def __init__(self, position: Position):
        self.decay = 0
        self.position = position

    def tick(self):
        self.decay += 1

        if self.decay > 255:
            self.decay = 0 # eventually will raise a destroy flag

    def render(self, camera, screen):
        if camera.is_in_view(*self.position.get_position()):
            pygame.draw.circle(screen, (255-self.decay,food_decay_yellow(self.decay),0), camera.world_to_screen(*self.position.get_position()), 5 * camera.zoom)
