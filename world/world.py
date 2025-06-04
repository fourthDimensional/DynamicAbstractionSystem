from collections import defaultdict
from abc import ABC, abstractmethod


class World:
    def __init__(self, partition_size=10):
        self.partition_size = partition_size
        self.buffers = [defaultdict(list), defaultdict(list)]
        self.current_buffer = 0

    def _hash_position(self, position):
        # Map world coordinates to cell coordinates
        return int(position.x // self.partition_size), int(
            position.y // self.partition_size
        )

    def render_all(self, camera, screen):
        for obj_list in self.buffers[self.current_buffer].values():
            for obj in obj_list:
                obj.render(camera, screen)

    def tick_all(self):
        next_buffer = 1 - self.current_buffer
        self.buffers[next_buffer].clear()

        # print all objects in the current buffer
        print(
            f"Ticking objects in buffer {self.current_buffer}:",
            self.buffers[self.current_buffer].values(),
        )

        for obj_list in self.buffers[self.current_buffer].values():
            for obj in obj_list:
                if obj.flags["death"]:
                    continue
                if obj.flags["can_interact"]:
                    interactable = self.query_objects_within_radius(
                        obj.position.x, obj.position.y, obj.interaction_radius
                    )
                    interactable.remove(obj)
                    print(f"Object {obj} interacting with {len(interactable)} objects.")
                    new_obj = obj.tick(interactable)
                else:
                    new_obj = obj.tick()
                if new_obj is None:
                    continue
                cell = self._hash_position(new_obj.position)
                self.buffers[next_buffer][cell].append(new_obj)
        self.current_buffer = next_buffer

    def add_object(self, new_object):
        cell = self._hash_position(new_object.position)
        self.buffers[self.current_buffer][cell].append(new_object)

    def query_objects_within_radius(self, x, y, radius):
        result = []
        cell_x, cell_y = int(x // self.partition_size), int(y // self.partition_size)
        cells_to_check = []
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

    def query_objects_in_range(self, x1, y1, x2, y2):
        result = []
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

    def query_closest_object(self, x, y):
        closest_obj = None
        closest_distance = float("inf")
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

    def get_objects(self):
        all_objects = []
        for obj_list in self.buffers[self.current_buffer].values():
            all_objects.extend(obj_list)
        print("All objects: ", all_objects)
        return all_objects

class BaseEntity(ABC):
    def __init__(self, position: "Position"):
        self.position = position
        self.interaction_radius = 0
        self.flags = {
            "death": False,
            "can_interact": False,
        }
        self.world_callbacks = {}
        self.max_visual_width = 0

    @abstractmethod
    def tick(self, interactable=None):
        return self

    @abstractmethod
    def render(self, camera, screen):
        pass

    def flag_for_death(self):
        self.flags["death"] = True

class Position:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __repr__(self):
        return f"Position({self.x}, {self.y})"

    def set_position(self, x, y):
        self.x = x
        self.y = y

    def get_position(self):
        return self.x, self.y
