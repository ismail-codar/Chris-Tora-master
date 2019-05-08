import json
from typing import List

import numpy as np

from helpers import get_average_percentage_deviation
from input_data.load_vendors import load_vendors, Vendor
from input_data.products import load_product_spec

NUMBER_OF_SCENARIOS = 2


def create_scenarios():
    vendor_path = "../input_data/deliveries.xlsx"
    vendors: List[Vendor] = load_vendors(path=vendor_path, adjust_delivery_estimate=0)
    product_specs = load_product_spec()

    for scenario_number in range(NUMBER_OF_SCENARIOS):
        results = []
        for vendor in vendors:
            for delivery in vendor.deliveries:
                for product in delivery.supply:

                    actual_delivery_volume = _draw_actual_volume(
                        estimated_volume=product.volume,
                        average_percentage_deviation=get_average_percentage_deviation(
                            product_specs=product_specs, product_type=product.product_type
                        )
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


def _draw_actual_volume(estimated_volume: float, average_percentage_deviation: float) -> float:
    variance = estimated_volume * average_percentage_deviation / 100
    standard_deviation = variance ** 1/2
    actual_volume = int(np.random.normal(loc=estimated_volume, scale=standard_deviation))
    if actual_volume < 0:
        return 0
    else:
        return actual_volume


create_scenarios()
