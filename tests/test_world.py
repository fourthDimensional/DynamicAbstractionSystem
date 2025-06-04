import pytest
from world.world import World, Position, BaseEntity


class DummyEntity(BaseEntity):
    def __init__(self, position):
        super().__init__(position)
        self.ticked = False
        self.rendered = False

    def tick(self, interactable=None):
        self.ticked = True
        return self

    def render(self, camera, screen):
        self.rendered = True


@pytest.fixture
def world():
    return World(partition_size=10, world_size=(100, 100))


def test_add_object_and_get_objects(world):
    entity = DummyEntity(Position(x=0, y=0))
    world.add_object(entity)
    assert entity in world.get_objects()


def test_query_objects_within_radius(world):
    e1 = DummyEntity(Position(x=0, y=0))
    e2 = DummyEntity(Position(x=5, y=0))
    e3 = DummyEntity(Position(x=20, y=0))
    world.add_object(e1)
    world.add_object(e2)
    world.add_object(e3)
    found = world.query_objects_within_radius(0, 0, 10)
    assert e1 in found
    assert e2 in found
    assert e3 not in found


def test_query_objects_in_range(world):
    e1 = DummyEntity(Position(x=1, y=1))
    e2 = DummyEntity(Position(x=5, y=5))
    e3 = DummyEntity(Position(x=20, y=20))
    world.add_object(e1)
    world.add_object(e2)
    world.add_object(e3)
    found = world.query_objects_in_range(0, 0, 10, 10)
    assert e1 in found
    assert e2 in found
    assert e3 not in found


def test_query_closest_object(world):
    e1 = DummyEntity(Position(x=0, y=0))
    e2 = DummyEntity(Position(x=10, y=0))
    world.add_object(e1)
    world.add_object(e2)
    closest = world.query_closest_object(1, 0)
    assert closest == e1


def test_tick_all_removes_dead(world):
    e1 = DummyEntity(Position(x=0, y=0))
    e2 = DummyEntity(Position(x=10, y=0))
    e2.flags["death"] = True
    world.add_object(e1)
    world.add_object(e2)
    world.tick_all()
    objs = world.get_objects()
    assert e1 in objs
    assert e2 not in objs


def test_tick_all_calls_tick(world):
    e1 = DummyEntity(Position(x=0, y=0))
    world.add_object(e1)
    world.tick_all()
    assert e1.ticked


def test_add_object_out_of_bounds(world):
    entity = DummyEntity(Position(x=1000, y=1000))
    with pytest.raises(ValueError):
        world.add_object(entity)
