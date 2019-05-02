from typing import List

from helpers import get_vendor_from_id, get_product_with_product_type
from input_data.load_vendors import Vendor
from scenarios.load_scenarios import Scenario


def update_todays_deliveries(vendors: List[Vendor], scenario: Scenario, current_day: int):
    for product_outcome in scenario.product_outcomes:
        vendor = get_vendor_from_id(vendors, product_outcome.vendor_id)
        delivery = vendor.deliveries[product_outcome.delivery_index]
        if delivery.arrival_day == current_day:
            product_type = product_outcome.product_type
            product = get_product_with_product_type(products=delivery.supply, product_type=product_type)
            product.volume = product_outcome.actual_volume
