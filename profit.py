from typing import List

from helpers import get_order_from_id, get_customer_from_id, \
    get_product_spec_from_product_type, get_transport_price_for_customer_c, get_customs_costs_for_product_p, get_transport_price_from_vendor_v
from input_data.load_customers import Customer, Order
from input_data.load_vendors import Vendor, Delivery
from input_data.products import ProductSpec
from optimize.objective_function import get_price_for_product_p
from optimize.optimize import Action
from optimize.constraints import TERMINAL_COST, QUANTITY_FULL_ORDER


def calculate_profit(
        customers: List[Customer],
        vendors: List[Vendor],
        product_specs: List[ProductSpec],
        todays_actions: List[Action],
) -> float:
    profit_for_realized_results = [
        _calculate_profit_for_one_action(
            action=action,
            customers=customers,
            product_specs=product_specs,
        )
        for action in todays_actions
    ]

    oslo_terminal_costs = [
        _calculate_oslo_cost(vendor=vendor, delivery=delivery, order=order, actions=todays_actions)
        for vendor in vendors
        for delivery in vendor.deliveries
        for customer in customers
        for order in customer.orders
    ]

    total_profit = sum(profit_for_realized_results) - sum(oslo_terminal_costs)
    return total_profit


def _calculate_profit_for_one_action(
        action: Action,
        customers: List[Customer],
        product_specs: List[ProductSpec],
) -> float:

    customer: Customer = get_customer_from_id(customer_id=action.customer_id, customers=customers)
    order: Order = get_order_from_id(orders=customer.orders, order_nr=action.order_nr)

    product_spec = get_product_spec_from_product_type(product_type=action.product_type, product_specs=product_specs,)
    
    price = get_price_for_product_p(
        product_type=action.product_type,
        products=order.demand
    )
    sales_revenue = price * action.volume_delivered

    if not action.internal_delivery:
        extra_cost_per_volume = product_spec.extra_cost
        cost_from_competitor = extra_cost_per_volume * action.volume_delivered
    else:
        cost_from_competitor = 0

    transportation_cost_to_customer = get_transport_price_for_customer_c(
        product_type=action.product_type,
        transportation_price_per_box=customer.transportation_price_per_box,
        customer_id=action.customer_id,
    )

    if customer.out_of_country:
        customs_cost = get_customs_costs_for_product_p(product_type=action.product_type, product_specs=product_specs,)
    else:
        customs_cost = 0

    profit = sales_revenue - cost_from_competitor - transportation_cost_to_customer - customs_cost

    return profit


def _calculate_oslo_cost(actions: List[Action], vendor: Vendor, delivery: Delivery, order: Order) -> float:
    relevant_actions_to_order_from_delivery = [
        action
        for action in actions
        if action.order_nr == order.order_number and action.delivery_number == delivery.delivery_number
    ]
    action_volumes_to_order_from_delivery = [
        action.volume_delivered
        for action in relevant_actions_to_order_from_delivery
    ]

    total_volume = sum(action_volumes_to_order_from_delivery)

    if total_volume < QUANTITY_FULL_ORDER:
        transportation_costs_per_action = [
            _get_transportation_cost_for_action(vendor=vendor, action=action)
            for action in relevant_actions_to_order_from_delivery
        ]
        total_cost = sum(transportation_costs_per_action)

    else:
        total_cost = 0

    return total_cost


def _get_transportation_cost_for_action(vendor: Vendor, action: Action):
    transportation_cost_from_vendor = get_transport_price_from_vendor_v(
        product_type=action.product_type,
        transportation_price_per_box=vendor.transportation_cost_per_box,
        vendor_id=action.vendor_id
    )
    volume = action.volume_delivered

    transport_cost = (transportation_cost_from_vendor + TERMINAL_COST) * volume

    return transport_cost

