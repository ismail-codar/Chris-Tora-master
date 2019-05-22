import time
from typing import List

from input_data.load_customers import load_customers
from input_data.load_vendors import load_vendors, Vendor
from input_data.products import load_product_spec
from optimize.optimize import start_optimize
from profit import _calculate_oslo_cost
from scenarios.load_scenarios import load_scenarios

from simulation.start_simulation import _filter_out_order_out_of_time_scope, run_simulation
from simulation.stochastic import optimize_with_one_product_type_at_the_time
from solution_method import SolutionMethod


SIMULATE_RESULTS = True
NUMBER_OF_SCENARIOS = 10
START_DAY = 1
END_DAY = 15
ADJUST_DELIVERY_ESTIMATE = 0 # Percent, 0 % -> no change
NUMBER_OF_DAYS_IN_EACH_RUN = 2
SOLUTION_METHOD = SolutionMethod.STOCHASTIC
ONE_PRODUCT_TYPE_AT_THE_TIME = True


def start_run():

    if SOLUTION_METHOD == SolutionMethod.STOCHASTIC and not ONE_PRODUCT_TYPE_AT_THE_TIME:
        raise Exception("If you do a stochastic run, you can only do one product type at the time")

    customers = load_customers()
    product_specs = load_product_spec()

    if SIMULATE_RESULTS:
        scenarios = load_scenarios(number_of_scenarios=NUMBER_OF_SCENARIOS)
        number_of_runs_in_one_scenario = (END_DAY - START_DAY) - NUMBER_OF_DAYS_IN_EACH_RUN + 2

        run_simulation(
            customers=customers,
            number_of_runs_in_one_scenario=number_of_runs_in_one_scenario,
            product_specs=product_specs,
            scenarios=scenarios,
            start_day=START_DAY,
            number_of_days_in_each_run=NUMBER_OF_DAYS_IN_EACH_RUN,
            solution_method=SOLUTION_METHOD,
            one_product_type_at_the_time=ONE_PRODUCT_TYPE_AT_THE_TIME,
            adjust_delivery_estimate=ADJUST_DELIVERY_ESTIMATE,
            end_day=END_DAY,
        )

    else:
        vendors = load_vendors(
            path="input_data/deliveries.xlsx",
            adjust_delivery_estimate=ADJUST_DELIVERY_ESTIMATE,
        )
        start_day = START_DAY
        print("Start day: " + str(start_day))
        end_day = start_day + NUMBER_OF_DAYS_IN_EACH_RUN - 1
        print("End day: " + str(end_day))
        vendors_with_relevant_deliveries = _filter_out_deliveries_out_of_time_scope(
            vendors=vendors,
            end_day=end_day,
            start_day=START_DAY
        )
        customers_with_relevant_orders = _filter_out_order_out_of_time_scope(
            customers=customers,
            start_day=start_day,
            end_day=end_day,
        )
        start_time = time.time()
        if ONE_PRODUCT_TYPE_AT_THE_TIME:
            actions, objective_value_without_cross_docking = optimize_with_one_product_type_at_the_time(
                vendors=vendors_with_relevant_deliveries,
                customers=customers_with_relevant_orders,
                product_specs=product_specs,
                solution_method=SOLUTION_METHOD,
                number_of_days_in_each_run=NUMBER_OF_DAYS_IN_EACH_RUN,
                start_day=start_day,
            )
            oslo_terminal_costs = sum([
                _calculate_oslo_cost(vendor=vendor, delivery=delivery, order=order, actions=actions)
                for vendor in vendors_with_relevant_deliveries
                for delivery in vendor.deliveries
                for customer in customers_with_relevant_orders
                for order in customer.orders
            ])
            objective_value = objective_value_without_cross_docking - oslo_terminal_costs
        else:
            actions, objective_value = start_optimize(
                vendors=vendors_with_relevant_deliveries,
                customers=customers_with_relevant_orders,
                product_specs=product_specs,
                solution_method=SOLUTION_METHOD,
                number_of_days_in_each_run=NUMBER_OF_DAYS_IN_EACH_RUN,
                start_day=start_day,
                include_cross_docking=True,
            )
        print("Objective value: " + str(objective_value))
        end_time = time.time()
        total_time = end_time - start_time
        print("Run time: " + str(total_time) + " sec")


def _filter_out_deliveries_out_of_time_scope(vendors: List[Vendor], start_day: int, end_day: int) -> List[Vendor]:
    vendors_with_only_relevant_deliveries = [
        Vendor(
            id=vendor.id,
            transportation_cost_per_box=vendor.transportation_cost_per_box,
            deliveries=[
                delivery
                for delivery in vendor.deliveries
                if start_day <= delivery.arrival_day <= end_day
            ]
        )
        for vendor in vendors
    ]
    return vendors_with_only_relevant_deliveries


start_run()
