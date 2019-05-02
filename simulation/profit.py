from typing import List

from input_data.load_customers import Customer, Order
from input_data.load_vendors import Vendor, Delivery
from input_data.products import ProductSpec, ProductType
from optimize.objective_function import get_price_for_product_p
from optimize.optimize import RealizedResult


def calculate_profit_for_start_day(
        customers: List[Customer],
        start_day: int,
        vendors: List[Vendor],
        product_specs: List[ProductSpec],
        realized_results: List[RealizedResult],
) -> float:

    total_revenue = 0
    total_cost = 0

    for realized_result in realized_results:
        customer: Customer = _get_element_from_id(element_id=realized_result.customer_id, elements=customers)
        order: Order = _get_order_from_id(orders=customer.orders, order_nr=realized_result.order_nr)

        if realized_result.internal_delivery:
            vendor = next(
                vendor
                for vendor in vendors
                if vendor.id == realized_result.vendor_id
            )
            delivery = next(
                delivery
                for delivery in vendor.deliveries
                if delivery.delivery_number == realized_result.delivery_number
            )

        price = get_price_for_product_p(
            product_type=realized_result.product_type,
            products=order.demand
        )
        revenue = price * realized_result.volume_delivered
        total_revenue += revenue

        product_spec = _get_product_spec_from_product_type(
            product_type=realized_result.product_type,
            product_specs=product_specs,
        )

        if not realized_result.internal_delivery:
            extra_cost_per_volume = product_spec.extra_cost
            extra_cost = extra_cost_per_volume * realized_result.volume_delivered
            total_cost += extra_cost

    profit = total_revenue - total_cost
    return profit


def _get_product_spec_from_product_type(product_type: ProductType, product_specs: List[ProductSpec]):
    return next(
        product_spec
        for product_spec in product_specs
        if product_spec.product_type == product_type
    )


def _get_element_from_id(element_id, elements):
    return next(
        element
        for element in elements
        if element.id == element_id
    )


def _get_order_from_id(order_nr, orders):
    return next(
        order
        for order in orders
        if order.order_number == order_nr
    )
