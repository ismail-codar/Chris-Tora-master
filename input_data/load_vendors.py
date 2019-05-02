from dataclasses import dataclass
from typing import List

from input_data.products import ProductType, Product, get_product_type
import xlrd


@dataclass(frozen=True)
class DeliveryLineInput:
    vendor_id: str
    delivery_number: int
    volume: int
    product_type: ProductType
    arrival_day: int
    price: float


@dataclass(frozen=True)
class TransportationCost:
    product_type: ProductType
    cost: float


@dataclass(frozen=True)
class TransportationCostInput:
    product_type: ProductType
    cost: float
    vendor_id: str


@dataclass(frozen=True)
class Delivery:
    arrival_day: int
    supply: List[Product]
    delivery_number: int


@dataclass(frozen=True)
class Vendor:
    id: str
    deliveries: List[Delivery]
    transportation_cost_per_box: List[TransportationCost]


def load_vendors(path):
    workbook = xlrd.open_workbook(path)
    delivery_sheet = workbook.sheet_by_index(0)
    cell_values_deliveries = delivery_sheet._cell_values
    del cell_values_deliveries[0]
    delivery_lines = [
        DeliveryLineInput(
            vendor_id=delivery_row[0],
            delivery_number=int(delivery_row[1]),
            volume=int(delivery_row[2]),
            product_type=get_product_type(product_type=delivery_row[3]),
            price=delivery_row[4],
            arrival_day=int(delivery_row[5]),
        )
        for delivery_row in cell_values_deliveries
    ]

    transportation_sheet = workbook.sheet_by_index(1)
    cell_values_transportation_cost = transportation_sheet._cell_values
    del cell_values_transportation_cost[0]
    transportation_costs = [
        TransportationCostInput(
            vendor_id=transportation_row[0],
            product_type=get_product_type(product_type=transportation_row[1]),
            cost=transportation_row[2]
        )
        for transportation_row in cell_values_transportation_cost
     ]
    vendor_sheet = workbook.sheet_by_index(2)
    cell_values_vendors = vendor_sheet._cell_values
    del cell_values_vendors[0]
    vendors = [
        _load_vendor(vendor_row, delivery_lines, transportation_costs)
        for vendor_row in cell_values_vendors
    ]
    return vendors


def _load_vendor(vendor_row, delivery_lines: List[DeliveryLineInput], transportation_costs: List[TransportationCostInput]):
    vendor_id = vendor_row[0]
    deliveries = _get_deliveries_belonging_to_vendor(vendor_id, delivery_lines)
    transportation_costs_from_vendor = [
        TransportationCost(
            product_type=transportation_cost.product_type,
            cost=transportation_cost.cost,
        )
        for transportation_cost in transportation_costs
        if transportation_cost.vendor_id == vendor_id
    ]
    vendor = Vendor(
        id=vendor_id,
        deliveries=deliveries,
        transportation_cost_per_box=transportation_costs_from_vendor,
    )
    return vendor


def _get_deliveries_belonging_to_vendor(vendor_id, delivery_lines: List[DeliveryLineInput]):
    delivery_lines_belonging_to_vendor = [
        delivery_line
        for delivery_line in delivery_lines
        if delivery_line.vendor_id == vendor_id
    ]
    unique_delivery_numbers = set([
        delivery_line.delivery_number
        for delivery_line in delivery_lines_belonging_to_vendor
    ])
    delivery_lines_per_delivery_number = [
        [
            delivery_line
            for delivery_line in delivery_lines_belonging_to_vendor
            if delivery_line.delivery_number == delivery_number
        ]
        for delivery_number in unique_delivery_numbers
    ]
    deliveries = [
        _create_delivery(
            delivery_lines_for_one_delivery_number=delivery_lines_for_delivery_number,
        )
        for delivery_lines_for_delivery_number in delivery_lines_per_delivery_number
    ]
    return deliveries


def _create_delivery(delivery_lines_for_one_delivery_number: List[DeliveryLineInput]):
    supply = [
        Product(
            product_type=delivery_line.product_type,
            volume=delivery_line.volume,
            price=delivery_line.price,
        )
        for delivery_line in delivery_lines_for_one_delivery_number
    ]

    delivery = Delivery(
        arrival_day=delivery_lines_for_one_delivery_number[0].arrival_day,
        supply=supply,
        delivery_number=delivery_lines_for_one_delivery_number[0].delivery_number,
    )
    return delivery
