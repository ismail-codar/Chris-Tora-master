from dataclasses import dataclass
from enum import Enum


class ProductType(Enum):
    SALMON_1_2 = 0
    SALMON_2_3 = 1
    # SALMON_3_4 = 2
    # SALMON_4_5 = 3
    # SALMON_5_6 = 4
    # SALMON_6_7 = 5
    # SALMON_7_8 = 6
    # SALMON_8_9 = 7


def get_product_type(product_type: str):
    if product_type == "fisk1til2":
        return ProductType.SALMON_1_2
    if product_type == "fisk2til3":
        return ProductType.SALMON_2_3
    if product_type == "fisk3til4":
        return ProductType.SALMON_3_4
    else:
        raise Exception("Unknown product type")


@dataclass(frozen=True)
class Product:
    product_type: ProductType
    volume: int
    price: float


@dataclass(frozen=True)
class ProductSpec:
    product_type: ProductType
    customs_cost: float
    extra_cost: float


def load_product_spec():
    product_specs = [
        ProductSpec(
            product_type=ProductType.SALMON_1_2,
            customs_cost=20.0,
            extra_cost=80.0,
        ),
        ProductSpec(
            product_type=ProductType.SALMON_2_3,
            customs_cost=20.0,
            extra_cost=80.0,
        ),
        # ProductSpec(
        #     product_type=ProductType.SALMON_3_4,
        #     customs_cost=20.0,
        #     extra_cost=80.0,
        # ),
        # ProductSpec(
        #     product_type=ProductType.SALMON_4_5,
        #     customs_cost=20.0,
        #     extra_cost=80.0,
        # ),
        # ProductSpec(
        #     product_type=ProductType.SALMON_5_6,
        #     customs_cost=20.0,
        #     extra_cost=80.0,
        # ),
        # ProductSpec(
        #     product_type=ProductType.SALMON_6_7,
        #     customs_cost=20.0,
        #     extra_cost=80.0,
        # ),
        # ProductSpec(
        #     product_type=ProductType.SALMON_7_8,
        #     customs_cost=20.0,
        #     extra_cost=80.0,
        # ),
        # ProductSpec(
        #     product_type=ProductType.SALMON_8_9,
        #     customs_cost=20.0,
        #     extra_cost=80.0,
        # )
    ]
    return product_specs
