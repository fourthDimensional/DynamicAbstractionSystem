from world.behavorial import BehavioralModel


class TestBrain(BehavioralModel):
    def __init__(self):
        super().__init__()
        # Define input keys
        self.inputs = {
            'distance': 0.0,  # Distance from a food object
            'angle': 0.0  # Relative angle to a food object
        }

        # Define output keys
        self.outputs = {
            'acceleration': 0.0,  # Linear acceleration
            'angular_acceleration': 0.0  # Angular acceleration
        }

        self.weights = {
            'distance': 1.0,
            'angle': 1.0
        }

    def tick(self, input_data) -> dict:
        """
        Process inputs and produce corresponding outputs.

        :param input_data: Dictionary containing 'distance' and 'angle' values
        :return: Dictionary with 'acceleration' and 'angular_acceleration' values
        """
        # Update internal input state
        self.inputs['distance'] = input_data.get('distance', 0.0)
        self.inputs['angle'] = input_data.get('angle', 0.0)

        # Initialize output dictionary
        output_data = {
            'acceleration': 0.0,
            'angular_acceleration': 0.0
        }

        return output_data
