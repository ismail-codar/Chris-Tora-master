from dataclasses import dataclass
from typing import List

from input_data.customer_category import CustomerCategory
from input_data.load_customers import Customer
from input_data.load_vendors import Vendor
from input_data.products import ProductSpec


@dataclass(frozen=True)
class Variables:
    x: list
    z: list
    t: list
    d: list
    y: list
    o: list


def create_variables_and_set_on_solver(
        vendors: List[Vendor],
        customers: List[Customer],
        solver,
        product_specs: List[ProductSpec],
        number_of_scenarios: int,
):
    x_vars = _create_x_vars(
        vendors=vendors,
        customers=customers,
        solver=solver,
        product_specs=product_specs,
        number_of_scenarios=number_of_scenarios,
    )
    z_vars = _create_z_vars(
        vendors=vendors,
        customers=customers,
        solver=solver,
        number_of_scenarios=number_of_scenarios,
    )
    t_vars = _create_t_vars(
        customers=customers,
        solver=solver,
        product_specs=product_specs,
        number_of_scenarios=number_of_scenarios,
    )
    d_vars = _create_d_vars(
        vendors=vendors,
        customers=customers,
        solver=solver,
        number_of_scenarios=number_of_scenarios,
    )
    y_vars = _create_y_vars(
        customers=customers,
        solver=solver,
        product_specs=product_specs,
        number_of_scenarios=number_of_scenarios,
    )
    o_vars = _create_o_vars(
        vendors=vendors,
        customers=customers,
        solver=solver,
        number_of_scenarios=number_of_scenarios,
    )

    variables = Variables(
        x=x_vars,
        z=z_vars,
        t=t_vars,
        d=d_vars,
        y=y_vars,
        o=o_vars,
    )
    return variables


# o oslo cost
def _create_o_vars(vendors: List[Vendor], customers: List[Customer], solver, number_of_scenarios: int):
    o_vars = [
        [
            [
                [
                    [
                        solver.NumVar(
                            lb=0,
                            ub=solver.infinity(),
                            name="o" +
                                 "_s:" + str(scenario) +
                                 "_v:" + vendor.id +
                                 "_d:" + str(delivery_index) +
                                 "_c:" + customer.id +
                                 "_o:" + str(order.order_number)
                        )
                        for order in customer.orders
                    ]
                    for customer in customers
                ]
                for delivery_index, delivery in enumerate(vendor.deliveries)
            ]
            for vendor in vendors
        ]
        for scenario in range(number_of_scenarios)
    ]
    return o_vars


# t = 1 if B-order is allowed to get any boxes
def _create_t_vars (
    customers: List[Customer],
    solver,
    product_specs: List[ProductSpec],
    number_of_scenarios: int
):
    t_vars = [
        [
            [
                [
                    solver.BoolVar(
                        name="t" +
                             "_s:" + str(scenario) +
                             "_c:" + customer.id +
                             "_o:" + str(order.order_number) +
                             "_p:" + str(product_spec.product_type.name)
                    )
                    for product_spec in product_specs
                ]
                for order in customer.orders
            ]
            for customer in customers
        ]
        for scenario in range(number_of_scenarios)
    ]
    return t_vars


# d = 1 if the order is sent directly to the customer
def _create_d_vars(vendors: List[Vendor], customers: List[Customer], solver, number_of_scenarios: int):
    d_vars = [
        [
            [
                [
                    [
                        solver.BoolVar(
                            name="d" +
                                 "_s:" + str(scenario) +
                                 "_v:" + vendor.id +
                                 "_d:" + str(delivery_index) +
                                 "_c:" + customer.id +
                                 "_o:" + str(order.order_number)
                        )
                        for order in customer.orders
                    ]
                    for customer in customers
                ]
                for delivery_index, delivery in enumerate(vendor.deliveries)
            ]
            for vendor in vendors
        ]
        for scenario in range(number_of_scenarios)
    ]
    return d_vars


# flow of extra delivery
def _create_y_vars(
    customers: List[Customer],
    solver,
    product_specs: List[ProductSpec],
    number_of_scenarios: int,
):
    y_vars = [
        [
            [
                [
                    solver.IntVar(
                        lb=0,
                        ub=solver.infinity(),
                        name="y" +
                             "_s:" + str(scenario) +
                             "_c:" + customer.id +
                             "_o:" + str(order.order_number) +
                             "_p:" + str(product_spec.product_type.name)
                    )
                    for product_spec in product_specs
                ]
                for order in customer.orders
            ]
            for customer in customers
        ]
        for scenario in range(number_of_scenarios)
    ]
    return y_vars


# z = 1 if order receives fish from delivery d
def _create_z_vars(vendors: List[Vendor], customers: List[Customer], solver, number_of_scenarios: int):
    z_vars = [
        [
            [
                [
                    [
                        solver.BoolVar(
                            name="z" +
                                 "_s" + str(scenario) +
                                 "_v:" + vendor.id +
                                 "_d:" + str(delivery_index) +
                                 "_c:" + customer.id +
                                 "_o:" + str(order.order_number)
                        )
                        for order in customer.orders
                    ]
                    for customer in customers
                ]
                for delivery_index, delivery in enumerate(vendor.deliveries)
            ]
            for vendor in vendors
        ]
        for scenario in range(number_of_scenarios)
    ]
    return z_vars


# flow of fish
def _create_x_vars(
        vendors: List[Vendor],
        customers: List[Customer],
        solver,
        product_specs: List[ProductSpec],
        number_of_scenarios: int,
):
    x_vars = [
        [
            [
                [
                    [
                        [
                            solver.IntVar(
                                lb=0,
                                ub=solver.infinity(),
                                name="x" +
                                     "_s:" + str(scenario) +
                                     "_v:" + vendor.id +
                                     "_d:" + str(delivery_index) +
                                     "_c:" + customer.id +
                                     "_o:" + str(order.order_number) +
                                     "_p:" + str(product_spec.product_type.name)
                            )
                            for product_spec in product_specs
                        ]
                        for order in customer.orders
                    ]
                    for customer in customers
                ]
                for delivery_index, delivery in enumerate(vendor.deliveries)
            ]
            for vendor in vendors
        ]
        for scenario in range(number_of_scenarios)
    ]
    return x_vars
