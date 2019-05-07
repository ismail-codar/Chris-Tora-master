import json
from dataclasses import dataclass
from typing import List

from input_data.products import ProductType
NUMBER_OF_SCENARIOS = 2


@dataclass(frozen=True)
class ProductScenarioOutcome:
    product_type: ProductType
    actual_volume: int
    vendor_id: str
    delivery_number: int


@dataclass(frozen=True)
class Scenario:
    product_outcomes: List[ProductScenarioOutcome]


def load_scenarios():
    scenarios = [
        _load_scenario(scenario_index)
        for scenario_index in range(NUMBER_OF_SCENARIOS)
    ]
    return scenarios


def _load_scenario(scenario_index: int) -> Scenario:

    path = "scenarios/scenario" + str(scenario_index) + ".json"

    with open(path) as file:
        scenario_dicts = json.loads(file.read())

    scenario = Scenario(
        [
            ProductScenarioOutcome(
                product_type=get_product_type(product_scenario_outcome["product_type"]),
                actual_volume=product_scenario_outcome["actual_delivery_volume"],
                vendor_id=product_scenario_outcome["vendor_id"],
                delivery_number=product_scenario_outcome["delivery_number"]
            )
            for product_scenario_outcome in scenario_dicts["results"]
        ]
    )
    return scenario


def get_product_type(product_type: str):
    if product_type == "SALMON_1_2":
        return ProductType.SALMON_1_2
    if product_type == "SALMON_2_3":
        return ProductType.SALMON_2_3
    if product_type == "SALMON_3_4":
        return ProductType.SALMON_3_4
    else:
        raise Exception("Unknown product type")
