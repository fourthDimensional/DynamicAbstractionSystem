from collections import defaultdict
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Optional, Any, TypeVar, Union
from pydantic import BaseModel, Field

T = TypeVar("T", bound="BaseEntity")


class Position(BaseModel):
    """
    Represents a 2D position in the world.
    """
    x: int = Field(..., description="X coordinate")
    y: int = Field(..., description="Y coordinate")

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def __repr__(self) -> str:
        return f"Position({self.x}, {self.y})"

    def set_position(self, x: int, y: int) -> None:
        """
        Sets the position to the given coordinates.

        :param x: New X coordinate.
        :param y: New Y coordinate.
        """
        self.x = x
        self.y = y

    def get_position(self) -> Tuple[int, int]:
        """
        Returns the current position as a tuple.

        :return: Tuple of (x, y).
        """
        return self.x, self.y


class BaseEntity(ABC):
    """
    Abstract base class for all entities in the world.
    """

    def __init__(self, position: Position) -> None:
        """
        Initializes the entity with a position.

        :param position: The position of the entity.
        """
        self.position: Position = position
        self.interaction_radius: int = 0
        self.flags: Dict[str, bool] = {
            "death": False,
            "can_interact": False,
        }
        self.world_callbacks: Dict[str, Any] = {}
        self.max_visual_width: int = 0

    @abstractmethod
    def tick(self, interactable: Optional[List["BaseEntity"]] = None) -> Optional["BaseEntity"]:
        """
        Updates the entity for a single tick.

        :param interactable: List of entities this entity can interact with.
        :return: The updated entity or None if it should be removed.
        """
        return self

    @abstractmethod
    def render(self, camera: Any, screen: Any) -> None:
        """
        Renders the entity on the screen.

        :param camera: The camera object for coordinate transformation.
        :param screen: The Pygame screen surface.
        """
        pass

    def flag_for_death(self) -> None:
        """
        Flags the entity for removal from the world.
        """
        self.flags["death"] = True


class World:
    """
    A world-class that contains and manages all objects in the game using spatial partitioning.
    """

    def __init__(self, partition_size: int = 10) -> None:
        """
        Initializes the world with a partition size.

        :param partition_size: The size of each partition cell in the world.
        """
        self.partition_size: int = partition_size
        self.buffers: List[Dict[Tuple[int, int], List[BaseEntity]]] = [defaultdict(list), defaultdict(list)]
        self.current_buffer: int = 0

    def _hash_position(self, position: Position) -> Tuple[int, int]:
        """
        Hashes a position into a cell based on the partition size.

        :param position: A Position object representing the position in the world.
        :return: Tuple (cell_x, cell_y) representing the cell coordinates.
        """
        return int(position.x // self.partition_size), int(position.y // self.partition_size)

    def render_all(self, camera: Any, screen: Any) -> None:
        """
        Renders all objects in the current buffer.

        :param camera: The camera object for coordinate transformation.
        :param screen: The Pygame screen surface.
        """
        for obj_list in self.buffers[self.current_buffer].values():
            for obj in obj_list:
                obj.render(camera, screen)

    def tick_all(self) -> None:
        """
        Advances all objects in the world by one tick, updating their state and handling interactions.
        """
        next_buffer: int = 1 - self.current_buffer
        self.buffers[next_buffer].clear()

        for obj_list in self.buffers[self.current_buffer].values():
            for obj in obj_list:
                if obj.flags["death"]:
                    continue
                if obj.flags["can_interact"]:
                    interactable = self.query_objects_within_radius(
                        obj.position.x, obj.position.y, obj.interaction_radius
                    )
                    interactable.remove(obj)
                    new_obj = obj.tick(interactable)
                else:
                    new_obj = obj.tick()
                if new_obj is None:
                    continue

                # reproduction code
                if isinstance(new_obj, list):
                    for item in new_obj:
                        if isinstance(item, BaseEntity):
                            cell = self._hash_position(item.position)
                            self.buffers[next_buffer][cell].append(item)
                else:
                    cell = self._hash_position(new_obj.position)
                    self.buffers[next_buffer][cell].append(new_obj)
        self.current_buffer = next_buffer

    def add_object(self, new_object: BaseEntity) -> None:
        """
        Adds a new object to the world in the appropriate cell.

        :param new_object: The object to add.
        """
        cell = self._hash_position(new_object.position)
        self.buffers[self.current_buffer][cell].append(new_object)

    def query_objects_within_radius(self, x: float, y: float, radius: float) -> List[BaseEntity]:
        """
        Returns all objects within a given radius of a point.

        :param x: X coordinate of the center.
        :param y: Y coordinate of the center.
        :param radius: Search radius.
        :return: List of objects within the radius.
        """
        result: List[BaseEntity] = []
        cell_x, cell_y = int(x // self.partition_size), int(y // self.partition_size)
        cells_to_check: List[Tuple[int, int]] = []
        r = int((radius // self.partition_size) + 1)
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                cells_to_check.append((cell_x + dx, cell_y + dy))
        for cell in cells_to_check:
            for obj in self.buffers[self.current_buffer].get(cell, []):
                obj_x, obj_y = obj.position.get_position()
                dx = obj_x - x
                dy = obj_y - y
                if dx * dx + dy * dy <= radius * radius:
                    result.append(obj)
        return result

    def query_objects_in_range(self, x1: float, y1: float, x2: float, y2: float) -> List[BaseEntity]:
        """
        Returns all objects within a rectangular range.

        :param x1: Minimum X coordinate.
        :param y1: Minimum Y coordinate.
        :param x2: Maximum X coordinate.
        :param y2: Maximum Y coordinate.
        :return: List of objects within the rectangle.
        """
        result: List[BaseEntity] = []
        cell_x1, cell_y1 = (
            int(x1 // self.partition_size),
            int(y1 // self.partition_size),
        )
        cell_x2, cell_y2 = (
            int(x2 // self.partition_size),
            int(y2 // self.partition_size),
        )
        for cell_x in range(cell_x1, cell_x2 + 1):
            for cell_y in range(cell_y1, cell_y2 + 1):
                for obj in self.buffers[self.current_buffer].get((cell_x, cell_y), []):
                    obj_x, obj_y = obj.position.get_position()
                    if x1 <= obj_x <= x2 and y1 <= obj_y <= y2:
                        result.append(obj)
        return result

    def query_closest_object(self, x: float, y: float) -> Optional[BaseEntity]:
        """
        Returns the closest object to a given point.

        :param x: X coordinate of the point.
        :param y: Y coordinate of the point.
        :return: The closest object or None if no objects exist.
        """
        closest_obj: Optional[BaseEntity] = None
        closest_distance: float = float("inf")
        for obj_list in self.buffers[self.current_buffer].values():
            for obj in obj_list:
                obj_x, obj_y = obj.position.get_position()
                dx = obj_x - x
                dy = obj_y - y
                distance = dx * dx + dy * dy
                if distance < closest_distance:
                    closest_distance = distance
                    closest_obj = obj
        return closest_obj

    def get_objects(self) -> List[BaseEntity]:
        """
        Returns a list of all objects currently in the world.

        :return: List of all objects.
        """
        all_objects: List[BaseEntity] = []
        for obj_list in self.buffers[self.current_buffer].values():
            all_objects.extend(obj_list)
        return all_objects