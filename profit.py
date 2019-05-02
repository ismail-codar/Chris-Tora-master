from typing import List

from helpers import get_vendor_from_id, get_delivery_from_del_number, get_order_from_id, get_customer_from_id, \
    get_product_spec_from_product_type
from input_data.load_customers import Customer, Order
from input_data.load_vendors import Vendor
from input_data.products import ProductSpec
from optimize.objective_function import get_price_for_product_p
from optimize.optimize import Action


def calculate_profit_for_start_day(
        customers: List[Customer],
        start_day: int,
        vendors: List[Vendor],
        product_specs: List[ProductSpec],
        actions: List[Action],
) -> float:

    profit_for_realized_results = [
        _calculate_profit_for_one_action(
            action=action,
            vendors=vendors,
            customers=customers,
            product_specs=product_specs,
        )
        for action in actions
        if action.transportation_day == start_day
    ]

    oslo_terminal_cost = _calculate_oslo_terminal_cost()

    total_profit = sum(profit_for_realized_results) - oslo_terminal_cost
    print("Profit for day " + str(start_day) + " is: " + str(total_profit))
    return total_profit


def _calculate_profit_for_one_action(
        action: Action,
        vendors: List[Vendor],
        customers: List[Customer],
        product_specs: List[ProductSpec],
) -> float:

    customer: Customer = get_customer_from_id(customer_id=action.customer_id, customers=customers)
    order: Order = get_order_from_id(orders=customer.orders, order_nr=action.order_nr)

    if action.internal_delivery:
        vendor = get_vendor_from_id(vendors=vendors, vendor_id=action.vendor_id)
        delivery = get_delivery_from_del_number(vendor.deliveries, action.delivery_number)

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

    profit = sales_revenue - cost_from_competitor

    return profit


def _calculate_oslo_terminal_cost() -> float:
    return 0
