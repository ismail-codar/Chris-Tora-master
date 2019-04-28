import uuid
from dataclasses import dataclass
from typing import List

from input_data.products import ProductType, Product


@dataclass(frozen=True)
class TransportationCost:
    product_type: ProductType
    cost: float


@dataclass(frozen=True)
class Delivery:
    delivery_day: int
    products: List[Product]
    id: str


@dataclass(frozen=True)
class Vendor:
    id: str
    deliveries: List[Delivery]
    transportation_cost_per_box: List[TransportationCost]


def load_vendors():
    vendors = _load_test_vendors()
    return vendors


def _load_test_vendors():
    delivery_1_vendor_1 = Delivery(
        delivery_day=1,
        products=[
            Product(
                product_type=ProductType.SALMON_1_2,
                volume=864,
                price=60.0
            ),
            Product(
                product_type=ProductType.SALMON_2_3,
                volume=864,
                price=60.0
            )
        ],
        id=str(uuid.uuid4())
    )

    vendor_1 = Vendor(
        id="vendor_1",
        deliveries=[
            delivery_1_vendor_1,
        ],
        transportation_cost_per_box=[
            TransportationCost(
                ProductType.SALMON_1_2,
                cost=2,
            ),
            TransportationCost(
                ProductType.SALMON_2_3,
                cost=3,
            )
        ]
    )

    delivery_1_vendor_2 = Delivery(
        delivery_day=1,
        products=[
            Product(
                product_type=ProductType.SALMON_2_3,
                volume=3,
                price=58.5,
            )
        ],
        id=str(uuid.uuid4()),
    )

    vendor_2 = Vendor(
        id="vendor_2",
        deliveries=[
            delivery_1_vendor_2,
        ],
        transportation_cost_per_box=[
            TransportationCost(
                ProductType.SALMON_1_2,
                cost=2,
            ),
            TransportationCost(
                ProductType.SALMON_2_3,
                cost=3,
            )
        ]
    )

    vendors = [vendor_1, vendor_2]
    return vendors
