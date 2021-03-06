from dataclasses import dataclass
from enum import Enum


class ProductType(Enum):
    SALMON_1_2 = 0
    SALMON_2_3 = 1
    SALMON_3_4 = 2
    SALMON_4_5 = 3
    SALMON_5_6 = 4
    SALMON_6_7 = 5
    SALMON_7_8 = 6
    SALMON_8_9 = 7
    SALMON_9 = 8

# Percentage
AVERAGE_DEVIATION_SALMON_1_2 = 37
AVERAGE_DEVIATION_SALMON_2_3 = 27.7
AVERAGE_DEVIATION_SALMON_3_4 = 21.2
AVERAGE_DEVIATION_SALMON_4_5 = 19.75
AVERAGE_DEVIATION_SALMON_5_6 = 23.19
AVERAGE_DEVIATION_SALMON_6_7 = 28.58
AVERAGE_DEVIATION_SALMON_7_8 = 33.67
AVERAGE_DEVIATION_SALMON_8_9 = 35.06
AVERAGE_DEVIATION_SALMON_9 = 40.46


def get_product_type(product_type: str):
    product_type_without_white_spaces = product_type.strip()
    if product_type_without_white_spaces == "1-2":
        return ProductType.SALMON_1_2
    if product_type_without_white_spaces == "2-3":
        return ProductType.SALMON_2_3
    if product_type_without_white_spaces == "3-4":
        return ProductType.SALMON_3_4
    if product_type_without_white_spaces == "4-5":
        return ProductType.SALMON_4_5
    if product_type_without_white_spaces == "5-6":
        return ProductType.SALMON_5_6
    if product_type_without_white_spaces == "6-7":
        return ProductType.SALMON_6_7
    if product_type_without_white_spaces == "7-8":
        return ProductType.SALMON_7_8
    if product_type_without_white_spaces == "8-9":
        return ProductType.SALMON_8_9
    if product_type_without_white_spaces == "9+":
        return ProductType.SALMON_9
    else:
        raise Exception(product_type + "is an unknown product type. See file products.py")


@dataclass(frozen=False)
class Product:
    product_type: ProductType
    volume: int
    price: float


@dataclass(frozen=True)
class ProductSpec:
    product_type: ProductType
    customs_cost: float
    extra_cost: float
    average_deviation: float


def load_product_spec():
    product_specs = [
        ProductSpec(
            product_type=ProductType.SALMON_1_2,
            customs_cost=60.0,
            extra_cost=3347.0,
            average_deviation=AVERAGE_DEVIATION_SALMON_1_2
        ),
        ProductSpec(
            product_type=ProductType.SALMON_2_3,
            customs_cost=60.0,
            extra_cost=3487.0,
            average_deviation=AVERAGE_DEVIATION_SALMON_2_3
        ),
        ProductSpec(
            product_type=ProductType.SALMON_3_4,
            customs_cost=60.0,
            extra_cost=3334.0,
            average_deviation=AVERAGE_DEVIATION_SALMON_3_4
        ),
        ProductSpec(
            product_type=ProductType.SALMON_4_5,
            customs_cost=60.0,
            extra_cost=3653,
            average_deviation=AVERAGE_DEVIATION_SALMON_4_5,
        ),
        ProductSpec(
            product_type=ProductType.SALMON_5_6,
            customs_cost=60.0,
            extra_cost=3690.0,
            average_deviation=AVERAGE_DEVIATION_SALMON_5_6,
        ),
        ProductSpec(
            product_type=ProductType.SALMON_6_7,
            customs_cost=60.0,
            extra_cost=3717.0,
            average_deviation=AVERAGE_DEVIATION_SALMON_6_7,
        ),
        ProductSpec(
            product_type=ProductType.SALMON_7_8,
            customs_cost=60.0,
            extra_cost=3725.0,
            average_deviation=AVERAGE_DEVIATION_SALMON_7_8,
        ),
        ProductSpec(
            product_type=ProductType.SALMON_8_9,
            customs_cost=60.0,
            extra_cost=1713.0,
            average_deviation=AVERAGE_DEVIATION_SALMON_8_9,
        ),
        ProductSpec(
            product_type=ProductType.SALMON_9,
            customs_cost=60.0,
            extra_cost=1694.0,
            average_deviation=AVERAGE_DEVIATION_SALMON_9,
        )
    ]
    return product_specs




