import math
import random

from world.base.brain import CellBrain
from world.behavioral import BehavioralModel
from world.world import Position, BaseEntity, Rotation
import pygame
from typing import Optional, List, Any, Union

from world.utils import get_distance_between_objects

from math import atan2, degrees


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
        super().__init__(position, Rotation(angle=0))
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

def chance_to_grow(decay_rate):
    return ((2**(-20*(decay_rate-1)))*12.5)+0.1

def chance(percent):
    return random.random() < percent / 100


class FoodObject(BaseEntity):
    """
    Food object that decays over time and is rendered as a colored circle.
    """

    def __init__(self, position: Position) -> None:
        """
        Initializes the food object.

        :param position: The position of the food.
        """
        super().__init__(position, Rotation(angle=0))
        self.max_visual_width: int = 10
        self.decay: int = 0
        self.decay_rate: int = 1
        self.max_decay = 200
        self.interaction_radius: int = 50
        self.neighbors: int = 0
        self.flags: dict[str, bool] = {
            "death": False,
            "can_interact": True,
        }

    def tick(self, interactable: Optional[List[BaseEntity]] = None) -> Union["FoodObject", List["FoodObject"]]:
        """
        Updates the food object, increasing decay and flagging for death if decayed.

        :param interactable: List of nearby entities (unused).
        :return: Self
        """
        if interactable is None:
            interactable = []

        self.neighbors = len(interactable)

        if self.neighbors > 0:
            self.decay += self.decay_rate * (1 + (self.neighbors / 10))
        else:
            self.decay += self.decay_rate

        if self.decay > self.max_decay:
            self.decay = self.max_decay
            self.flag_for_death()

        grow_chance = chance_to_grow(self.decay_rate * (1 + (self.neighbors / 10)))

        # print(grow_chance)

        if chance(grow_chance):
            # print("Growing")
            duplicate_x, duplicate_y = self.position.get_position()
            duplicate_x += random.randint(-self.interaction_radius, self.interaction_radius)
            duplicate_y += random.randint(-self.interaction_radius, self.interaction_radius)

            return [self, FoodObject(Position(x=duplicate_x, y=duplicate_y))]

        return self

    def normalize_decay_to_color(self) -> int:
        """
        Normalizes the decay value to a color component.

        :return: Normalized decay value (0-255).
        """
        return self.decay / self.max_decay * 255 if self.max_decay > 0 else 0

    def render(self, camera: Any, screen: Any) -> None:
        """
        Renders the food object as a decaying colored circle.

        :param camera: The camera object for coordinate transformation.
        :param screen: The Pygame screen surface.
        """
        if camera.is_in_view(*self.position.get_position()):
            pygame.draw.circle(
                screen,
                (255 - self.normalize_decay_to_color(), food_decay_yellow(self.normalize_decay_to_color()), 0),
                camera.world_to_screen(*self.position.get_position()),
                int(5 * camera.zoom)
            )

    def __repr__(self) -> str:
        """
        Returns a string representation of the food object.

        :return: String representation.
        """
        return f"FoodObject({self.position}, decay={self.decay:.1f}, decay_rate={self.decay_rate * (1 + (self.neighbors / 10))})"


class TestVelocityObject(BaseEntity):
    """
    Test object that moves in a randomly set direction.
    """

    def __init__(self, position: Position) -> None:
        """
        Initializes the test velocity object.

        :param position: The position of the object.
        """
        super().__init__(position, Rotation(angle=random.randint(0, 360)))
        self.velocity = (random.uniform(-0.1, 0.5), random.uniform(-0.1, 0.5))
        self.max_visual_width: int = 10
        self.interaction_radius: int = 50
        self.flags: dict[str, bool] = {
            "death": False,
            "can_interact": True,
        }

    def tick(self, interactable: Optional[List[BaseEntity]] = None) -> "TestVelocityObject":
        """
        Updates the object by moving it according to its velocity.

        :param interactable: List of nearby entities (unused).
        :return: Self.
        """
        if interactable is None:
            interactable = []

        x, y = self.position.get_position()
        x += self.velocity[0]
        y += self.velocity[1]
        self.position.set_position(x, y)

        return self

    def render(self, camera: Any, screen: Any) -> None:
        """
        Renders the test object as a circle.

        :param camera: The camera object for coordinate transformation.
        :param screen: The Pygame screen surface.
        """
        if camera.is_in_view(*self.position.get_position()):
            pygame.draw.circle(
                screen,
                (0, 255, 0),
                camera.world_to_screen(*self.position.get_position()),
                int(5 * camera.zoom)
            )

    def __repr__(self) -> str:
        """
        Returns a string representation of the test object.

        :return: String representation.
        """
        return f"TestVelocityObject({self.position}, velocity={self.velocity})"


class DefaultCell(BaseEntity):
    """
    Cell object
    """
    def __init__(self, starting_position: Position, starting_rotation: Rotation) -> None:
        """
        Initializes the cell.

        :param starting_position: The position of the object.
        """

        super().__init__(starting_position, starting_rotation)
        self.drag_coefficient: float = 0.1

        self.velocity: tuple[int, int] = (0, 0)
        self.acceleration: tuple[int, int] = (0, 0)

        self.rotational_velocity: int = 0
        self.angular_acceleration: int = 0

        self.behavioral_model: CellBrain = CellBrain()

        self.max_visual_width: int = 10
        self.interaction_radius: int = 50
        self.flags: dict[str, bool] = {
            "death": False,
            "can_interact": True,
        }


    def set_brain(self, behavioral_model: CellBrain) -> None:
        self.behavioral_model = behavioral_model


    def tick(self, interactable: Optional[List[BaseEntity]] = None) -> "DefaultCell":
        """
        Updates the cell according to its behavioral model.

        :param interactable: List of nearby entities (unused).
        :return: Self.
        """
        if interactable is None:
            interactable = []

        # filter interactable objects
        food_objects = self.filter_food(interactable)

        # grab the closest food
        if len(food_objects) > 0:
            food_object = food_objects[0]
        else:
            food_object = FoodObject(self.position)

        angle_between_food = self.calculate_angle_between_food(self.position.get_position(), self.rotation.get_rotation(), food_object.position.get_position())

        input_data = {
            "distance": get_distance_between_objects(self, food_object),
            "angle": angle_between_food,
        }

        output_data = self.behavioral_model.tick(input_data)

        # clamp accelerations
        output_data["linear_acceleration"] = max(-0.1, min(0.02, output_data["linear_acceleration"]))
        output_data["angular_acceleration"] = max(-0.1, min(0.1, output_data["angular_acceleration"]))

        # output acceleration is acceleration along its current rotation.
        x_component = output_data["linear_acceleration"] * math.cos(math.radians(self.rotation.get_rotation()))
        y_component = output_data["linear_acceleration"] * math.sin(math.radians(self.rotation.get_rotation()))

        self.acceleration = (x_component, y_component)
        
        # # add drag according to current velocity
        # drag_coefficient = 0.3
        # drag_x = -self.velocity[0] * drag_coefficient
        # drag_y = -self.velocity[1] * drag_coefficient
        # self.acceleration = (self.acceleration[0] + drag_x, self.acceleration[1] + drag_y)

        # tick acceleration
        velocity_x = self.velocity[0] + self.acceleration[0]
        velocity_y = self.velocity[1] + self.acceleration[1]
        self.velocity = (velocity_x, velocity_y)

        # clamp velocity
        self.velocity = (max(-0.5, min(0.5, self.velocity[0])), max(-0.5, min(0.5, self.velocity[1])))

        # tick velocity
        x, y = self.position.get_position()
        x += self.velocity[0]
        y += self.velocity[1]

        self.position.set_position(x, y)

        # tick rotational acceleration
        self.angular_acceleration = output_data["angular_acceleration"]
        self.rotational_velocity += self.angular_acceleration

        # clamp rotational velocity
        self.rotational_velocity = max(-0.5, min(0.5, self.rotational_velocity))

        # tick rotational velocity
        self.rotation.set_rotation(self.rotation.get_rotation() + self.rotational_velocity)

        return self

    @staticmethod
    def calculate_angle_between_food(object_position, object_rotation, food_position) -> float:
        """
		Calculates the angle between an object's current rotation and the position of the food.

		:param object_position: Tuple of (x, y) for the object's position.
		:param object_rotation: Current rotation of the object in degrees.
		:param food_position: Tuple of (x, y) for the food's position.
		:return: Angle between -180 and 180 degrees.
		"""
        obj_x, obj_y = object_position
        food_x, food_y = food_position

        # Calculate the angle to the food relative to the object
        angle_to_food = math.degrees(math.atan2(food_y - obj_y, food_x - obj_x))

        # Calculate the relative angle to the object's rotation
        angle_between = angle_to_food - object_rotation

        # Normalize the angle to be between -180 and 180 degrees
        if angle_between > 180:
            angle_between -= 360
        elif angle_between < -180:
            angle_between += 360

        return angle_between

    def filter_food(self, input_objects: List[BaseEntity]) -> List[FoodObject]:
        """
        Filters the input objects to only include food. Sort output by distance, closest first
        """
        food_objects = []
        for obj in input_objects:
            if isinstance(obj, FoodObject):
                food_objects.append(obj)
        food_objects.sort(key=lambda x: get_distance_between_objects(self, x))
        return food_objects

    def render(self, camera: Any, screen: Any) -> None:
        """
        Renders the cell as a circle.

        :param camera: The camera object for coordinate transformation.
        :param screen: The Pygame screen surface.
        """
        if camera.is_in_view(*self.position.get_position()):
            pygame.draw.circle(
                screen,
                (0, 255, 0),
                camera.world_to_screen(*self.position.get_position()),
                int(5 * camera.zoom)
            )

    def __repr__(self):
        position = f"({round(self.position.x, 1)}, {round(self.position.y, 1)})"
        velocity = tuple(round(value, 1) for value in self.velocity)
        acceleration = tuple(round(value, 1) for value in self.acceleration)
        return f"DefaultCell(position={position}, velocity={velocity}, acceleration={acceleration}, behavioral_model={self.behavioral_model})"
