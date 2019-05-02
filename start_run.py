from typing import List

from helpers import get_vendor_from_id, get_product_with_product_type, get_delivery_from_del_number
from input_data.load_customers import load_customers, Customer
from input_data.load_vendors import load_vendors, Vendor
from input_data.products import load_product_spec
from optimize.optimize import start_optimize, Action
from profit import calculate_profit_for_start_day
from scenarios.load_scenarios import load_scenarios, Scenario
import timeit

DETERMINISTIC = True
SIMULATE_RESULTS = True
NUMBER_OF_DAYS_IN_EACH_RUN = 5
TIME_HORIZON = 15
START_DAY = 1

ADJUST_DELIVERY_ESTIMATE = 0 # Percent, 0 % -> no change


def start_run():

    customers = load_customers()
    product_specs = load_product_spec()

    if SIMULATE_RESULTS:
        scenarios = load_scenarios()
        number_of_runs_in_one_scenario = TIME_HORIZON - NUMBER_OF_DAYS_IN_EACH_RUN + 1

        profit_for_scenarios = []
        average_time_for_scenarios = []

        for scenario_index, scenario in enumerate(scenarios):
            vendors = load_vendors(
                path="input_data/deliveries.xlsx",
                adjust_delivery_estimate=ADJUST_DELIVERY_ESTIMATE
            )
            current_start_day = START_DAY
            profits_for_scenario = []
            times_for_runs = []

            for run_number in range(number_of_runs_in_one_scenario):

                current_end_day = current_start_day + NUMBER_OF_DAYS_IN_EACH_RUN

                update_todays_deliveries_based_on_actual_volume_in_scenario(
                    vendors=vendors,
                    scenario=scenario,
                    current_day=current_start_day,
                )
                vendors_with_relevant_deliveries_for_next_run = _filter_out_deliveries_after_end_time(
                    vendors=vendors,
                    end_day=current_end_day,
                )
                customers_with_relevant_orders_for_next_run = _filter_out_order_out_of_time_scope(
                    customers=customers,
                    start_day=current_start_day,
                    end_day=current_end_day,
                )
                start = timeit.timeit()
                actions = start_optimize(
                    vendors=vendors_with_relevant_deliveries_for_next_run,
                    customers=customers_with_relevant_orders_for_next_run,
                    product_specs=product_specs,
                )
                end = timeit.timeit()
                total_time = end - start
                times_for_runs.append(total_time)

                actions_with_delivery_date_today = [
                    action
                    for action in actions
                    if action.transportation_day == current_start_day
                ]
                profit_from_todays_operation = calculate_profit_for_start_day(
                    vendors=vendors,
                    customers=customers,
                    product_specs=product_specs,
                    actions=actions_with_delivery_date_today,
                    start_day=current_start_day,
                )
                profits_for_scenario.append(profit_from_todays_operation)

                update_delivery_volumes_after_todays_operations(
                    vendors=vendors,
                    todays_actions=actions_with_delivery_date_today,
                )
                current_start_day += 1

            profit_for_scenario = sum(profit_for_scenarios)
            average_time_for_scenario = sum(times_for_runs) / number_of_runs_in_one_scenario
            print("profit for scenario " + str(scenario_index) + ": " + str(profit_for_scenario))
            profit_for_scenarios.append(profit_for_scenario)

            average_time_for_scenarios.append(average_time_for_scenario)

        average_run_time = sum(average_time_for_scenarios) / len(scenarios)
        print("Average run time: " + str(average_run_time))
        average_profit = sum(profit_for_scenarios) / len(profit_for_scenarios)
        print("Average profit is: " + str(average_profit))


    else:
        vendors = load_vendors(
            path="input_data/deliveries.xlsx",
            adjust_delivery_estimate=ADJUST_DELIVERY_ESTIMATE,
        )
        start_day = START_DAY
        end_day = start_day + NUMBER_OF_DAYS_IN_EACH_RUN
        vendors_with_relevant_deliveries = _filter_out_deliveries_after_end_time(
            vendors=vendors,
            end_day=end_day,
        )
        customers_with_relevant_orders = _filter_out_order_out_of_time_scope(
            customers=customers,
            start_day=start_day,
            end_day=end_day,
        )
        actions = start_optimize(
            vendors=vendors_with_relevant_deliveries,
            customers=customers_with_relevant_orders,
            product_specs=product_specs,
        )
        profit_for_start_day = calculate_profit_for_start_day(
            vendors=vendors_with_relevant_deliveries,
            customers=customers_with_relevant_orders,
            product_specs=product_specs,
            actions=actions,
            start_day=start_day,
        )


def _filter_out_deliveries_after_end_time(vendors: List[Vendor], end_day: int) -> List[Vendor]:
    vendors_with_only_relevant_deliveries = [
        Vendor(
            id=vendor.id,
            transportation_cost_per_box=vendor.transportation_cost_per_box,
            deliveries=[
                delivery
                for delivery in vendor.deliveries
                if delivery.arrival_day <= end_day
            ]
        )
        for vendor in vendors
    ]
    return vendors_with_only_relevant_deliveries


def _filter_out_order_out_of_time_scope(customers: List[Customer], start_day: int, end_day: int) -> List[Customer]:
    customer_with_only_relevant_deliveries = [
        Customer(
            id=customer.id,
            orders=[
                order
                for order in customer.orders
                if start_day <= order.departure_day <= end_day
            ],
            customer_category=customer.customer_category,
            out_of_country=customer.out_of_country,
            transportation_price_per_box=customer.transportation_price_per_box
        )
        for customer in customers
    ]
    return customer_with_only_relevant_deliveries


def update_todays_deliveries_based_on_actual_volume_in_scenario(vendors: List[Vendor], scenario: Scenario, current_day: int):
    for product_outcome in scenario.product_outcomes:
        vendor = get_vendor_from_id(vendors, product_outcome.vendor_id)
        delivery = vendor.deliveries[product_outcome.delivery_index]
        if delivery.arrival_day == current_day:
            product_type = product_outcome.product_type
            product = get_product_with_product_type(products=delivery.supply, product_type=product_type)
            product.volume = product_outcome.actual_volume


def update_delivery_volumes_after_todays_operations(vendors: List[Vendor], todays_actions: List[Action]):
    for action in todays_actions:
        if action.internal_delivery:
            vendor = get_vendor_from_id(vendors, action.vendor_id)
            delivery = get_delivery_from_del_number(deliveries=vendor.deliveries, delivery_number=action.delivery_number)

            product = get_product_with_product_type(products=delivery.supply, product_type=action.product_type)
            product.volume -= action.volume_delivered


start_run()
