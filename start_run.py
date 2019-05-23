import time
from typing import List

from input_data.load_customers import load_customers, Customer
from input_data.load_vendors import load_vendors, Vendor
from input_data.products import load_product_spec, ProductSpec
from optimize.optimize import start_optimize
from scenarios.load_scenarios import load_scenarios

from simulation.start_simulation import _filter_out_order_out_of_time_scope, run_simulation
from simulation.stochastic import optimize_with_one_product_type_at_the_time
from solution_method import SolutionMethod


SIMULATE_RESULTS = False
NUMBER_OF_SCENARIOS = 10
START_DAY = 1
TIME_HORIZON = 15
ADJUST_DELIVERY_ESTIMATE = 0 # Percent, 0 % -> no change
NUMBER_OF_DAYS_IN_EACH_RUN = 4
SOLUTION_METHOD = SolutionMethod.DETERMINISTIC
ONE_PRODUCT_TYPE_AT_THE_TIME = False
NAME = "Kristine"


def start_run():
    print("simulate results: " + str(SIMULATE_RESULTS))
    print("Start day: " + str(START_DAY))
    print("Time horizon: " + str(TIME_HORIZON))
    print("adjust delivery estimate: " + str(ADJUST_DELIVERY_ESTIMATE))
    print("Solution method: " + str(SOLUTION_METHOD.name))
    print("One product at the time: " + str(ONE_PRODUCT_TYPE_AT_THE_TIME))

    for number_of_days in range(1, 2):

        print("number of days: " + str(NUMBER_OF_DAYS_IN_EACH_RUN))

        if SOLUTION_METHOD == SolutionMethod.STOCHASTIC and not ONE_PRODUCT_TYPE_AT_THE_TIME:
            raise Exception("If you do a stochastic run, you can only do one product type at the time")

        customers = load_customers()
        product_specs = load_product_spec()

        if SIMULATE_RESULTS:
            scenarios = load_scenarios(number_of_scenarios=NUMBER_OF_SCENARIOS)

            run_simulation(
                customers=customers,
                number_of_runs_in_one_scenario=TIME_HORIZON,
                product_specs=product_specs,
                scenarios=scenarios,
                start_day=START_DAY,
                number_of_days_in_each_run=NUMBER_OF_DAYS_IN_EACH_RUN,
                solution_method=SOLUTION_METHOD,
                one_product_type_at_the_time=ONE_PRODUCT_TYPE_AT_THE_TIME,
                adjust_delivery_estimate=ADJUST_DELIVERY_ESTIMATE,
                time_horizon=TIME_HORIZON,
                name=NAME,
            )

        else:
            _run_one_optimization(
                customers=customers,
                product_specs=product_specs,
                start_day=START_DAY,
                adjusted_delivery_estimate=ADJUST_DELIVERY_ESTIMATE,
                number_of_days_in_each_run=NUMBER_OF_DAYS_IN_EACH_RUN,
                time_horizon=TIME_HORIZON,
                one_product_at_the_time=ONE_PRODUCT_TYPE_AT_THE_TIME,
                solution_method=SOLUTION_METHOD,
            )


def _run_one_optimization(
        customers: List[Customer],
        product_specs: List[ProductSpec],
        start_day: int,
        adjusted_delivery_estimate: float,
        number_of_days_in_each_run: int,
        time_horizon: int,
        one_product_at_the_time: bool,
        solution_method: SolutionMethod,
):
    vendors = load_vendors(
        path="input_data/deliveries.xlsx",
        adjust_delivery_estimate=adjusted_delivery_estimate,
    )
    print("Start day: " + str(start_day))
    end_day = min(start_day + number_of_days_in_each_run - 1, start_day + time_horizon - 1)
    print("End day: " + str(end_day))
    vendors_with_relevant_deliveries = _filter_out_deliveries_out_of_time_scope(
        vendors=vendors,
        end_day=end_day,
        start_day=start_day
    )
    customers_with_relevant_orders = _filter_out_order_out_of_time_scope(
        customers=customers,
        start_day=start_day,
        end_day=end_day,
    )

    start_time = time.time()
    if one_product_at_the_time:
        optimize_results = optimize_with_one_product_type_at_the_time(
            vendors=vendors_with_relevant_deliveries,
            customers=customers_with_relevant_orders,
            product_specs=product_specs,
            solution_method=SOLUTION_METHOD,
            number_of_days_in_each_run=number_of_days_in_each_run,
            start_day=start_day,
            simulation=False,
        )
    else:
        optimize_results = start_optimize(
            vendors=vendors_with_relevant_deliveries,
            customers=customers_with_relevant_orders,
            product_specs=product_specs,
            solution_method=solution_method,
            number_of_days_in_each_run=number_of_days_in_each_run,
            start_day=start_day,
            include_cross_docking=True,
            simulation=False,
        )
    print("Objective value: " + str(optimize_results.objective_value))
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
