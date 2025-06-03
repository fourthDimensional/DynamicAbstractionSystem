from world.world import Position, BaseEntity
import pygame


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
