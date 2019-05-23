from typing import List

from input_data.load_customers import Customer, Order
from input_data.load_vendors import Vendor, Delivery
from input_data.products import ProductSpec, ProductType, Product
from optimize.optimize import Action, start_optimize, OptimizeResults
from profit import _calculate_oslo_cost
from solution_method import SolutionMethod


def optimize_with_one_product_type_at_the_time(
    vendors: List[Vendor],
    customers: List[Customer],
    product_specs: List[ProductSpec],
    solution_method: SolutionMethod,
    number_of_days_in_each_run: int,
    start_day: int,
    simulation: bool,
) -> List[Action]:

    all_actions: List[Action] = []
    objective_value_without_terminal_cost = 0
    number_of_constraints = 0
    number_of_variables = 0

    for product_spec in product_specs:

        current_product_type = product_spec.product_type

        customers_with_demand_only_for_current_product_type = _filter_out_demand_for_other_product_types_from_customers(
            customers=customers, product_type=current_product_type,
        )
        demand_volume = sum([
            demand.volume
            for customer in customers_with_demand_only_for_current_product_type
            for order in customer.orders
            for demand in order.demand
        ])
        if len(customers_with_demand_only_for_current_product_type) > 0:
            print("Optimize for product" + str(product_spec.product_type.name))
            vendors_with_supply_only_for_current_product_type = _filter_out_supply_for_other_product_types_from_vendors(
                vendors=vendors, product_type=current_product_type,
            )
            supply_volume = sum([
                supply.volume
                for vendor in vendors_with_supply_only_for_current_product_type
                for delivery in vendor.deliveries
                for supply in delivery.supply
            ])
            print("Demand volume: " + str(demand_volume))
            print("Supply volume: " + str(supply_volume))
            optimize_results_for_one_product = start_optimize(
                vendors=vendors_with_supply_only_for_current_product_type,
                customers=customers_with_demand_only_for_current_product_type,
                product_specs=[product_spec],
                solution_method=solution_method,
                number_of_days_in_each_run=number_of_days_in_each_run,
                start_day=start_day,
                include_cross_docking=False,
                simulation=simulation,
            )
            objective_value_without_terminal_cost += optimize_results_for_one_product.objective_value
            all_actions.extend(optimize_results_for_one_product.actions)
            number_of_constraints += optimize_results_for_one_product.number_of_constraints
            number_of_variables += optimize_results_for_one_product.number_of_variables

    if simulation:
        oslo_terminal_costs = sum([
            _calculate_oslo_cost(vendor=vendor, delivery=delivery, order=order, actions=all_actions)
            for vendor in vendors
            for delivery in vendor.deliveries
            for customer in customers
            for order in customer.orders
        ])
    else:
        oslo_terminal_costs = 0
    optimize_results = OptimizeResults(
        actions=all_actions,
        objective_value=objective_value_without_terminal_cost - oslo_terminal_costs,
        number_of_variables=number_of_variables,
        number_of_constraints=number_of_constraints,
    )

    return optimize_results


def _filter_out_demand_for_other_product_types_from_customers(customers: List[Customer], product_type: ProductType) -> List[Customer]:
    customers_without_demand_for_other_product_types = [
        Customer(
            id=customer.id,
            orders=_filter_out_other_product_types_from_orders(
                orders=customer.orders, product_type=product_type
            ),
            customer_category=customer.customer_category,
            out_of_country=customer.out_of_country,
            transportation_price_per_box=customer.transportation_price_per_box
        )
        for customer in customers
    ]
    only_relevant_customers = [
        customer
        for customer in customers_without_demand_for_other_product_types
        if len(customer.orders) > 0
    ]
    return only_relevant_customers


def _filter_out_other_product_types_from_orders(orders: List[Order], product_type: ProductType) -> List[Order]:
    orders_without_demand_for_other_product_types = [
        Order(
            departure_day=order.departure_day,
            demand=_filter_out_other_product_types(products=order.demand, product_type=product_type),
            order_number=order.order_number,
        )
        for order in orders
    ]
    only_relevant_orders = [
        order
        for order in orders_without_demand_for_other_product_types
        if len(order.demand) > 0
    ]
    return only_relevant_orders


def _filter_out_other_product_types(products: List[Product], product_type: ProductType) -> List[Product]:
    return [
        product
        for product in products
        if product.product_type == product_type
    ]


def _filter_out_supply_for_other_product_types_from_vendors(vendors: List[Vendor], product_type: ProductType) -> List[Vendor]:
    vendors_without_supply_for_other_products = [
        Vendor(
            id=vendor.id,
            deliveries=_filter_out_other_product_types_from_deliveries(
                deliveries=vendor.deliveries, product_type=product_type
            ),
            transportation_cost_per_box=vendor.transportation_cost_per_box,
        )
        for vendor in vendors
    ]
    only_relevant_vendors = [
        vendor
        for vendor in vendors_without_supply_for_other_products
        if len(vendor.deliveries) > 0
    ]
    return only_relevant_vendors


def _filter_out_other_product_types_from_deliveries(deliveries: List[Delivery], product_type: ProductType) -> List[Delivery]:
    deliveries_without_supplies_for_other_products = [
        Delivery(
            supply=_filter_out_other_product_types(products=delivery.supply, product_type=product_type),
            arrival_day=delivery.arrival_day,
            delivery_number=delivery.delivery_number,
        )
        for delivery in deliveries
    ]
    only_relevant_deliveries = [
        delivery
        for delivery in deliveries_without_supplies_for_other_products
        if len(delivery.supply) > 0
    ]

    return only_relevant_deliveries
