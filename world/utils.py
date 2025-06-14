def get_distance_between_objects(object_a, object_b):
    return ((object_a.position.x - object_b.position.x)**2 + (object_a.position.y - object_b.position.y)**2)**0.5