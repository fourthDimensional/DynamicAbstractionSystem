class World:
    def __init__(self):
        self.objects = []
        pass

    def render_all(self, camera, screen):
        for obj in self.objects:
            obj.render(camera, screen)

    def tick_all(self):
        for obj in self.objects:
            obj.tick()

    def add_object(self, new_object):
        self.objects.append(new_object)

    def get_objects(self):
        return self.objects

class Position:
    def __init__(self, x, y):
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

