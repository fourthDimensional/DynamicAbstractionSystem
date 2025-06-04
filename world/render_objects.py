import random

from world.world import Position, BaseEntity
import pygame
from typing import Optional, List, Any


class DebugRenderObject(BaseEntity):
    """
    Debug object that renders as a circle and counts its neighbors.
    """

    def __init__(self, position: Position, radius: int = 5) -> None:
        """
        Initializes the debug render object.

        :param position: The position of the object.
        :param radius: The radius of the rendered circle.
        """
        super().__init__(position)
        self.neighbors: int = 0
        self.radius: int = radius
        self.max_visual_width: int = radius * 2
        self.interaction_radius: int = 50
        self.flags: dict[str, bool] = {
            "death": False,
            "can_interact": True,
        }

    def tick(self, interactable: Optional[List[BaseEntity]] = None) -> "DebugRenderObject":
        """
        Updates the object, counting the number of interactable neighbors.

        :param interactable: List of nearby entities.
        :return: Self.
        """
        if interactable is None:
            interactable = []
        self.neighbors = len(interactable)
        return self

    def render(self, camera: Any, screen: Any) -> None:
        """
        Renders the debug object as a circle, color intensity based on neighbors.

        :param camera: The camera object for coordinate transformation.
        :param screen: The Pygame screen surface.
        """
        if camera.is_in_view(*self.position.get_position()):
            pygame.draw.circle(
                screen,
                (50, 50, min([255, (self.neighbors + 4) * 30])),
                camera.world_to_screen(*self.position.get_position()),
                int(self.radius * camera.zoom),
            )

    def __repr__(self) -> str:
        """
        Returns a string representation of the object.

        :return: String representation.
        """
        return f"DebugRenderObject({self.position}, neighbors={self.neighbors})"


def food_decay_yellow(decay: int) -> int:
    """
    Returns the yellow color component for food decay visualization.

    :param decay: The current decay value (0-255).
    :return: The yellow component (0-255).
    """
    if decay < 128:
        return decay
    else:
        return 255 - decay


class FoodObject(BaseEntity):
    """
    Food object that decays over time and is rendered as a colored circle.
    """

    def __init__(self, position: Position) -> None:
        """
        Initializes the food object.

        :param position: The position of the food.
        """
        super().__init__(position)
        self.max_visual_width: int = 10
        self.decay: int = 0
        self.interaction_radius: int = 50
        self.flags: dict[str, bool] = {
            "death": False,
            "can_interact": True,
        }

    def tick(self, interactable: Optional[List[BaseEntity]] = None) -> Optional["FoodObject"]:
        """
        Updates the food object, increasing decay and flagging for death if decayed.

        :param interactable: List of nearby entities (unused).
        :return: Self
        """
        if interactable is None:
            interactable = []

        self.decay += 1

        if self.decay > 255:
            self.decay = 255
            self.flag_for_death()

        return self

    def render(self, camera: Any, screen: Any) -> None:
        """
        Renders the food object as a decaying colored circle.

        :param camera: The camera object for coordinate transformation.
        :param screen: The Pygame screen surface.
        """
        if camera.is_in_view(*self.position.get_position()):
            pygame.draw.circle(
                screen,
                (255 - self.decay, food_decay_yellow(self.decay), 0),
                camera.world_to_screen(*self.position.get_position()),
                int(5 * camera.zoom)
            )

    def __repr__(self) -> str:
        """
        Returns a string representation of the food object.

        :return: String representation.
        """
        return f"FoodObject({self.position}, decay={self.decay})"