import json
from dataclasses import dataclass
from typing import List

from input_data.products import ProductType


@dataclass(frozen=True)
class ProductScenarioOutcome:
    product_type: ProductType
    actual_volume: int
    vendor_id: str
    delivery_number: int


@dataclass(frozen=True)
class Scenario:
    product_outcomes: List[ProductScenarioOutcome]


def load_scenarios(number_of_scenarios: int):
    scenarios = [
        _load_scenario(scenario_index)
        for scenario_index in range(number_of_scenarios)
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
    if product_type == "SALMON_4_5":
        return ProductType.SALMON_4_5
    if product_type == "SALMON_5_6":
        return ProductType.SALMON_5_6
    if product_type == "SALMON_6_7":
        return ProductType.SALMON_6_7
    if product_type == "SALMON_7_8":
        return ProductType.SALMON_7_8
    if product_type == "SALMON_8_9":
        return ProductType.SALMON_8_9
    if product_type == "SALMON_9":
        return ProductType.SALMON_9
    else:
        raise Exception("Unknown product type")
