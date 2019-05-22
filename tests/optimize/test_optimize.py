from unittest import TestCase

from input_data.customer_category import CustomerCategory
from input_data.load_customers import Customer, Order, TransportationCost
from input_data.load_vendors import Vendor, Delivery
from input_data.products import Product, ProductType, ProductSpec
from optimize.optimize import start_optimize
from solution_method import SolutionMethod


class Optimize(TestCase):
    def test_case_in_optimize(self):

        order = Order(
            departure_day=0,
            demand=[Product(
                product_type=ProductType.SALMON_1_2,
                volume=100,
                price=12,
            )],
            order_number=0
        )

        customers = [
            Customer(
                id="test_customer",
                orders=[order],
                customer_category=CustomerCategory.Contract,
                out_of_country=False,
                transportation_price_per_box=[TransportationCost(
                    product_type=ProductType.SALMON_1_2,
                    cost=0,
                )]
            )
        ]

        delivery = Delivery(
            arrival_day=0,
            supply=[Product(
                product_type=ProductType.SALMON_1_2,
                volume=100,
                price=5,
            )],
            delivery_number=0,
        )

        vendors = [
            Vendor(
                id="test vendor",
                deliveries=[delivery],
                transportation_cost_per_box=[TransportationCost(
                    product_type=ProductType.SALMON_1_2,
                    cost=0,
                )]
            )
        ]
        product_specs = [
            ProductSpec(
                product_type=ProductType.SALMON_1_2,
                customs_cost=0,
                extra_cost=20,
                average_deviation=0.10,
            )
        ]
        actions, _ = start_optimize(
            vendors=vendors,
            customers=customers,
            product_specs=product_specs,
            solution_method=SolutionMethod.STOCHASTIC,
            number_of_days_in_each_run=2,
            start_day=0,
        )
