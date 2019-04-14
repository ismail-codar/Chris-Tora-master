from dataclasses import dataclass
from typing import List

from input_data.products import ProductType, Product


@dataclass(frozen=True)
class Delivery:
    delivery_day: int
    products: List[Product]
    transportation_cost_per_box: float


@dataclass(frozen=True)
class Vendor:
    id: str
    deliveries: List[Delivery]


def load_vendors():
    vendors = _load_test_vendors()
    return vendors


def _load_test_vendors():
    delivery_1_vendor_1 = Delivery(
        delivery_day=4,
        products=[
            Product(
                product_type=ProductType.SALMON_2_3,
                volume=4,
                price=58.9
            ),
            Product(
                product_type=ProductType.SALMON_1_2,
                volume=864,
                price=60.0
            )
        ],
        transportation_cost_per_box=0.5,
    )

    vendor_1 = Vendor(
        id="vendor_1",
        deliveries=[
            delivery_1_vendor_1,
        ]
    )

    delivery_1_vendor_2 = Delivery(
        delivery_day=4,
        products=[
            Product(
                product_type=ProductType.SALMON_2_3,
                volume=3,
                price=58.5,
            )
        ],
        transportation_cost_per_box=0.5,
    )

    vendor_2 = Vendor(
        id="vendor_2",
        deliveries=[
            delivery_1_vendor_2,
        ]
    )

    vendors = [vendor_1, vendor_2]
    return vendors
