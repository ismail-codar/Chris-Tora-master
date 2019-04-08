from dataclasses import dataclass
from typing import List

from input_data.customer_category import CustomerCategory, get_customer_category
from input_data.products import ProductType, Product, get_product_type
import xlrd


@dataclass(frozen=True)
class OrderLineInput:
    customer_id: str
    order_number: int
    volume: int
    product_type: ProductType
    departure_day: int
    price: float


@dataclass(frozen=True)
class Order:
    departure_day: int
    demand: List[Product]
    order_number: int


@dataclass(frozen=True)
class TransportationCostInput:
    product_type: ProductType
    cost: float
    customer_id: str


@dataclass(frozen=True)
class TransportationCost:
    product_type: ProductType
    cost: float


@dataclass(frozen=True)
class Customer:
    id: str
    orders: List[Order]
    customer_category: CustomerCategory
    out_of_country: bool
    transportation_price_per_box: List[TransportationCost]


def load_customers():
    path = ("../input_data/orders.xlsx")
    workbook = xlrd.open_workbook(path)
    order_sheet = workbook.sheet_by_index(0)
    cell_values_orders = order_sheet._cell_values
    del cell_values_orders[0]
    order_lines = [
        OrderLineInput(
            customer_id=order_row[0],
            order_number=int(order_row[1]),
            volume=int(order_row[2]),
            product_type=get_product_type(product_type=order_row[3]),
            departure_day=int(order_row[4]),
            price=order_row[5],
        )
        for order_row in cell_values_orders
    ]

    transportation_sheet = workbook.sheet_by_index(2)
    cell_values_transportation_cost = transportation_sheet._cell_values
    del cell_values_transportation_cost[0]
    transportation_costs = [
        TransportationCostInput(
            customer_id=transportation_row[0],
            product_type=get_product_type(product_type=transportation_row[1]),
            cost=transportation_row[2]
        )
        for transportation_row in cell_values_transportation_cost
    ]

    customer_sheet = workbook.sheet_by_index(1)
    cell_values_customers = customer_sheet._cell_values
    del cell_values_customers[0]
    customers = [
        _load_customer(customer_row, order_lines, transportation_costs)
        for customer_row in cell_values_customers
    ]
    return customers


def _load_customer(customer_row, order_lines: List[OrderLineInput], transportation_costs: List[TransportationCostInput]):
    customer_id = customer_row[0]
    orders = _get_orders_belonging_to_customer(customer_id, order_lines)
    transportation_costs_for_customer = [
        TransportationCost(
            product_type=transportation_cost.product_type,
            cost=transportation_cost.cost,
        )
        for transportation_cost in transportation_costs
        if transportation_cost.customer_id == customer_id
    ]
    customer = Customer(
        id=customer_id,
        orders=orders,
        customer_category=get_customer_category(customer_row[2]),
        out_of_country=True if customer_row[1] == 1 else False,
        transportation_price_per_box=transportation_costs_for_customer,
    )
    return customer


def _get_orders_belonging_to_customer(customer_id, order_lines: List[OrderLineInput]):
    order_lines_belonging_to_customer = [
        order_line
        for order_line in order_lines
        if order_line.customer_id == customer_id
    ]
    unique_order_numbers = set([
        order_line.order_number
        for order_line in order_lines_belonging_to_customer
    ])
    order_lines_per_order_number = [
        [
            order_line
            for order_line in order_lines_belonging_to_customer
            if order_line.order_number == order_number
        ]
        for order_number in unique_order_numbers
    ]
    orders = [
        _create_order(
            order_lines_for_one_order_number=order_lines_for_order_number,
        )
        for order_lines_for_order_number in order_lines_per_order_number
    ]
    return orders


def _create_order(order_lines_for_one_order_number: List[OrderLineInput]):
    demand = [
        Product(
            product_type=order_line.product_type,
            volume=order_line.volume,
            price=order_line.price,
        )
        for order_line in order_lines_for_one_order_number
    ]

    order = Order(
        departure_day=order_lines_for_one_order_number[0].departure_day,
        demand=demand,
        order_number=order_lines_for_one_order_number[0].order_number,
    )
    return order
