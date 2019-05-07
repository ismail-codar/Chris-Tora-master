import json
from typing import List

import numpy as np

from input_data.load_vendors import load_vendors, Vendor
from input_data.products import ProductType

NUMBER_OF_SCENARIOS = 2

# Percentage
AVERAGE_DEVIATION_SALMON_1_2 = 5.12
AVERAGE_DEVIATION_SALMON_2_3 = -3.28
AVERAGE_DEVIATION_SALMON_3_4 = -4.81
AVERAGE_DEVIATION_SALMON_4_5 = -0.54
AVERAGE_DEVIATION_SALMON_5_6 = -0.55
AVERAGE_DEVIATION_SALMON_6_7 = 2.95
AVERAGE_DEVIATION_SALMON_7_8 = 6.17
AVERAGE_DEVIATION_SALMON_8_9 = 9.14
AVERAGE_DEVIATION_SALMON_9 = 9.56


def create_scenarios():
    vendor_path = "../input_data/deliveries.xlsx"
    vendors: List[Vendor] = load_vendors(path=vendor_path, adjust_delivery_estimate=0)

    for scenario_number in range(NUMBER_OF_SCENARIOS):
        results = []
        for vendor in vendors:
            for delivery in vendor.deliveries:
                for product in delivery.supply:

                    actual_delivery_volume = _draw_actual_volume(
                        product_type=product.product_type,
                        estimated_volume=product.volume
                    )
                    result = {
                        "vendor_id": vendor.id,
                        "delivery_number": delivery.delivery_number,
                        "actual_delivery_volume": actual_delivery_volume,
                        "product_type": product.product_type.name
                    }
                    results.append(result)

        with open("scenario" + str(scenario_number) + ".json", "w") as file:
            json.dump({"results": results}, file)


def _draw_actual_volume(product_type: ProductType, estimated_volume: float) -> float:
    average_percentage_deviation = _get_average_percentage_deviation(product_type)
    variance = estimated_volume * average_percentage_deviation / 100
    standard_deviation = variance ** 1/2
    actual_volume = int(np.random.normal(loc=estimated_volume, scale=standard_deviation))
    if actual_volume < 0:
        return 0
    else:
        return actual_volume


def _get_average_percentage_deviation(product_type: ProductType) -> float:
    if product_type == ProductType.SALMON_1_2:
        return AVERAGE_DEVIATION_SALMON_1_2
    elif product_type == ProductType.SALMON_2_3:
        return AVERAGE_DEVIATION_SALMON_2_3
    elif product_type == ProductType.SALMON_3_4:
        return AVERAGE_DEVIATION_SALMON_3_4
    else:
        raise Exception("unknown product type")


create_scenarios()
