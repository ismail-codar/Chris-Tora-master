from typing import List

from input_data.load_customers import load_customers, Customer
from input_data.load_vendors import load_vendors, Vendor
from input_data.products import load_product_spec
from optimize.optimize import start_optimize
from scenarios.load_scenarios import load_scenarios
from simulation.profit import calculate_profit_for_start_day

DETERMINISTIC = True
SIMULATE_RESULTS = True
NUMBER_OF_DAYS_IN_EACH_RUN = 5
TIME_HORIZON = 15
START_DAY = 1


def start_run():

    vendors = load_vendors()
    customers = load_customers()
    product_specs = load_product_spec()

    if SIMULATE_RESULTS:
        scenarios = load_scenarios()
        number_of_runs = TIME_HORIZON - NUMBER_OF_DAYS_IN_EACH_RUN + 1

    start_day = START_DAY
    end_day = start_day + NUMBER_OF_DAYS_IN_EACH_RUN

    vendors_with_relevant_deliveries = _filter_out_deliveries_out_of_time_scope(
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
    stop = 4


def _filter_out_deliveries_out_of_time_scope(vendors: List[Vendor], end_day: int) -> List[Vendor]:
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


start_run()
