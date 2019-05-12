from unittest import TestCase

from optimize.objective_function import _get_probability_of_scenario


class TestConstraints(TestCase):
    def test_that_sum_all_all_scenario_probabilities_is_1(self):

        number_of_scenarios = 3 ** 5
        probabilities = [
            _get_probability_of_scenario(
                scenario_index=scenario_index,
                number_of_scenarios=number_of_scenarios,
                number_of_days_in_one_run=5,
            )
            for scenario_index in range(number_of_scenarios)
        ]
        total_probability = sum(probabilities)
        self.assertEqual(1, total_probability)
