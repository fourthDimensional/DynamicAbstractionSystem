from world.behavioral import BehavioralModel


class CellBrain(BehavioralModel):
    def __init__(self):
        super().__init__()
        # Define input keys
        self.inputs = {
            'distance': 0.0,  # Distance from a food object
            'angle': 0.0  # Relative angle to a food object
        }

        # Define output keys
        self.outputs = {
            'linear_acceleration': 0.0,  # Linear acceleration
            'angular_acceleration': 0.0  # Angular acceleration
        }

        self.weights = {
            'distance': 1,
            'angle': 0.5
        }

    def tick(self, input_data) -> dict:
        """
        Process inputs and produce corresponding outputs.

        :param input_data: Dictionary containing 'distance' and 'angle' values
        :return: Dictionary with 'linear_acceleration' and 'angular_acceleration' values
        """
        # Update internal input state
        self.inputs['distance'] = input_data.get('distance', 0.0)
        self.inputs['angle'] = input_data.get('angle', 0.0)

        # Initialize output dictionary
        output_data = {'linear_acceleration': self.inputs['distance'] * self.weights['distance'],
					   'angular_acceleration': self.inputs['angle'] * self.weights['angle']}

        self.outputs = output_data

        return output_data

    def __repr__(self):
        inputs = {key: round(value, 1) for key, value in self.inputs.items()}
        outputs = {key: round(value, 1) for key, value in self.outputs.items()}
        weights = {key: round(value, 1) for key, value in self.weights.items()}
        return f"CellBrain(inputs={inputs}, outputs={outputs}, weights={weights})"
