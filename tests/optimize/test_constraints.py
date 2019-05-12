from unittest import TestCase

from optimize.constraints import _get_supply_level_from_scenario_index
from optimize.non_anticipativity import _get_number_of_scenarios_to_groups_together


class TestConstraints(TestCase):
    def test_that_correct_supply_level_is_calculated_from_scenario_tree(self):

        actual_supply_level = _get_supply_level_from_scenario_index(
            arrival_day=1,
            number_of_days_in_one_run=3,
            scenario_index=25,
            start_day=1,
        )
        expected_supply_level = 2
        self.assertEqual(expected_supply_level, actual_supply_level)

        actual_supply_level = _get_supply_level_from_scenario_index(
            arrival_day=3,
            number_of_days_in_one_run=3,
            scenario_index=25,
            start_day=1,
        )
        expected_supply_level = 1
        self.assertEqual(expected_supply_level, actual_supply_level)

        actual_supply_level = _get_supply_level_from_scenario_index(
            arrival_day=2,
            number_of_days_in_one_run=3,
            scenario_index=25,
            start_day=1,
        )
        expected_supply_level = 2
        self.assertEqual(expected_supply_level, actual_supply_level)

        actual_supply_level = _get_supply_level_from_scenario_index(
            arrival_day=5,
            number_of_days_in_one_run=1,
            scenario_index=2,
            start_day=5,
        )
        expected_supply_level = 2
        self.assertEqual(expected_supply_level, actual_supply_level)

        actual_supply_level = _get_supply_level_from_scenario_index(
            arrival_day=5,
            number_of_days_in_one_run=3,
            scenario_index=0,
            start_day=5,
        )
        expected_supply_level = 0
        self.assertEqual(expected_supply_level, actual_supply_level)

        actual_supply_level = _get_supply_level_from_scenario_index(
            arrival_day=1,
            number_of_days_in_one_run=3,
            scenario_index=14,
            start_day=0,
        )
        expected_supply_level = 1
        self.assertEqual(expected_supply_level, actual_supply_level)

    def test_number_of_scenarios_to_groups_together(self):
        number_of_scenarios = 243

        actual_number_of_scenarios = _get_number_of_scenarios_to_groups_together(
            arrival_day_index=2,
            number_of_scenarios=number_of_scenarios
        )
        expected_number_of_scenarios_to_group_together = 243 / (3*3)
        self.assertEqual(expected_number_of_scenarios_to_group_together, actual_number_of_scenarios)

        actual_number_of_scenarios = _get_number_of_scenarios_to_groups_together(
            arrival_day_index=1,
            number_of_scenarios=number_of_scenarios
        )
        expected_number_of_scenarios_to_group_together = 243 / 3
        self.assertEqual(expected_number_of_scenarios_to_group_together, actual_number_of_scenarios)

        arrival_day_index = 0
        actual_number_of_scenarios = _get_number_of_scenarios_to_groups_together(
            arrival_day_index=arrival_day_index,
            number_of_scenarios=number_of_scenarios
        )
        expected_number_of_scenarios_to_group_together = 243
        self.assertEqual(expected_number_of_scenarios_to_group_together, actual_number_of_scenarios)

