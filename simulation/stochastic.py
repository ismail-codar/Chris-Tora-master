from typing import List

from input_data.load_customers import Customer, Order
from input_data.load_vendors import Vendor, Delivery
from input_data.products import ProductSpec, ProductType, Product
from optimize.optimize import Action, start_optimize


def optimize_with_one_product_type_at_the_time(
    vendors: List[Vendor],
    customers: List[Customer],
    product_specs: List[ProductSpec],
    stochastic: bool,
    number_of_days_in_each_run: int,
    start_day: int,
) -> List[Action]:

    all_actions = []

    for product_spec in product_specs:

        current_product_type = product_spec.product_type

        customers_with_demand_only_for_current_product_type = _filter_out_demand_for_other_product_types_from_customers(
            customers=customers, product_type=current_product_type,
        )
        demand_for_current_product_type = [
            demand
            for customer in customers_with_demand_only_for_current_product_type
            for order in customer.orders
            for demand in order.demand
        ]
        if len(demand_for_current_product_type) > 0:
            print("Optimize for product" + str(product_spec.product_type.name))
            vendors_with_supply_only_for_current_product_type = _filter_out_supply_for_other_product_types_from_vendors(
                vendors=vendors, product_type=current_product_type,
            )
            actions_for_current_product_type = start_optimize(
                vendors=vendors_with_supply_only_for_current_product_type,
                customers=customers_with_demand_only_for_current_product_type,
                product_specs=[product_spec],
                stochastic=stochastic,
                number_of_days_in_each_run=number_of_days_in_each_run,
                start_day=start_day,
            )
        else:
            actions_for_current_product_type = []
        all_actions.extend(actions_for_current_product_type)

    return all_actions


def _filter_out_demand_for_other_product_types_from_customers(customers: List[Customer], product_type: ProductType) -> List[Customer]:
    customers_with_only_relevant_orders = [
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
    return customers_with_only_relevant_orders


def _filter_out_other_product_types_from_orders(orders: List[Order], product_type: ProductType) -> List[Order]:
    orders_with_demand_only_for_product_type = [
        Order(
            departure_day=order.departure_day,
            demand=_filter_out_other_product_types(products=order.demand, product_type=product_type),
            order_number=order.order_number,
        )
        for order in orders
    ]
    return orders_with_demand_only_for_product_type


def _filter_out_other_product_types(products: List[Product], product_type: ProductType) -> List[Product]:
    return [
        product
        for product in products
        if product.product_type == product_type
    ]


def _filter_out_supply_for_other_product_types_from_vendors(vendors: List[Vendor], product_type: ProductType) -> List[Vendor]:
    vendors_with_only_relevant_deliveries = [
        Vendor(
            id=vendor.id,
            deliveries=_filter_out_other_product_types_from_deliveries(
                deliveries=vendor.deliveries, product_type=product_type
            ),
            transportation_cost_per_box=vendor.transportation_cost_per_box,
        )
        for vendor in vendors
    ]
    return vendors_with_only_relevant_deliveries


def _filter_out_other_product_types_from_deliveries(deliveries: List[Delivery], product_type: ProductType) -> List[Delivery]:
    deliveries_with_supply_only_for_product_type = [
        Delivery(
            supply=_filter_out_other_product_types(products=delivery.supply, product_type=product_type),
            arrival_day=delivery.arrival_day,
            delivery_number=delivery.delivery_number,
        )
        for delivery in deliveries
    ]
    return deliveries_with_supply_only_for_product_type
