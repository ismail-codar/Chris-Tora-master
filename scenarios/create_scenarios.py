import json
from typing import List

import numpy as np

from input_data.load_vendors import load_vendors, Vendor
from input_data.products import ProductType

NUMBER_OF_SCENARIOS = 2

# Long term
AVERAGE_DEVIATION_SALMON_1_2 = 10
AVERAGE_DEVIATION_SALMON_2_3 = 7


def create_scenarios():

    vendors: List[Vendor] = load_vendors()

    for scenario_number in range(NUMBER_OF_SCENARIOS):
        results = []
        for vendor in vendorfs:
            for delivery_index, delivery in enumerate(vendor.deliveries):
                for product in delivery.products:

                    product_type = product.product_type
                    estimated_volume = product.volume

                    if delivery.delivery_day == 0:
                        actual_delivery_volume = estimated_volume
                    else:
                        actual_delivery_volume = _draw_actual_volume(
                            product_type=product_type,
                            estimated_volume=estimated_volume
                        )
                    result = {
                        "vendor_id": vendor.id,
                        "delivery_index": delivery_index,
                        "actual_delivery_volume": actual_delivery_volume,
                        "product_type": product_type.name
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
    else:
        raise Exception("unknown product type")


create_scenarios()