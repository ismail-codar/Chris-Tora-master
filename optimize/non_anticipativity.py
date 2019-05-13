from typing import List

from input_data.load_customers import Customer
from input_data.load_vendors import Vendor
from input_data.products import ProductSpec


def set_non_anticipativity_constraints(
        variables,
        start_day: int,
        number_of_days_in_one_run: int,
        number_of_scenarios: int,
        solver,
        customers: List[Customer],
        vendors: List[Vendor],
        product_specs = List[ProductSpec],
):
    for arrival_day_index in range(number_of_days_in_one_run):
        arrival_day = start_day + arrival_day_index
        number_of_scenarios_to_groups_together = _get_number_of_scenarios_to_groups_together(
            arrival_day_index=arrival_day_index, number_of_scenarios=number_of_scenarios
        )
        number_of_clusters_for_this_day = number_of_scenarios / number_of_scenarios_to_groups_together
        if int(number_of_clusters_for_this_day) != number_of_clusters_for_this_day:
            raise Exception("Error non anticipativity constraints")
        for cluster_index in range(int(number_of_clusters_for_this_day)):
            _group_x_variables(
                cluster_index=cluster_index,
                x_vars=variables.x,
                number_of_scenarios_to_groups_together=number_of_scenarios_to_groups_together,
                arrival_day=arrival_day,
                solver=solver,
                customers=customers,
                vendors=vendors,
                product_specs=product_specs,
            )
            _group_y_variables(
                cluster_index=cluster_index,
                y_vars=variables.y,
                number_of_scenarios_to_groups_together=number_of_scenarios_to_groups_together,
                arrival_day=arrival_day,
                solver=solver,
                customers=customers,
                product_specs=product_specs,
            )


def _get_number_of_scenarios_to_groups_together(arrival_day_index: int, number_of_scenarios: int) -> int:
    if arrival_day_index == 0:
        number_of_days_to_group_together = number_of_scenarios
    else:
        number_of_days_to_group_together = number_of_scenarios / (3 ** arrival_day_index)
    return number_of_days_to_group_together


def _group_x_variables(
        x_vars,
        cluster_index: int,
        number_of_scenarios_to_groups_together: int,
        arrival_day: int,
        customers: List[Customer],
        vendors: List[Vendor],
        product_specs: List[ProductSpec],
        solver,
):
    start_scenario_index = int(number_of_scenarios_to_groups_together * cluster_index)
    end_scenario_index = int(start_scenario_index + number_of_scenarios_to_groups_together)

    for v, vendor in enumerate(vendors):
        for d, delivery in enumerate(vendor.deliveries):
            for c, customer in enumerate(customers):
                for o, order in enumerate(customer.orders):
                    if order.departure_day == arrival_day:
                        for p, product in enumerate(product_specs):

                            for s in range(start_scenario_index + 1, end_scenario_index):

                                x_non_anti = solver.Constraint(0, 0)
                                x_non_anti.SetCoefficient(x_vars[start_scenario_index][v][d][c][o][p], 1)
                                x_non_anti.SetCoefficient(x_vars[s][v][d][c][o][p], -1)


def _group_y_variables(
        y_vars,
        cluster_index: int,
        number_of_scenarios_to_groups_together: int,
        arrival_day: int,
        customers: List[Customer],
        product_specs: List[ProductSpec],
        solver,
):
    start_scenario_index = int(number_of_scenarios_to_groups_together * cluster_index)
    end_scenario_index = int(start_scenario_index + number_of_scenarios_to_groups_together)

    for c, customer in enumerate(customers):
        for o, order in enumerate(customer.orders):
            if order.departure_day == arrival_day:
                for p, product in enumerate(product_specs):

                    for s in range(start_scenario_index + 1, end_scenario_index):

                        x_non_anti = solver.Constraint(0, 0)
                        x_non_anti.SetCoefficient(y_vars[start_scenario_index][c][o][p], 1)
                        x_non_anti.SetCoefficient(y_vars[s][c][o][p], -1)
