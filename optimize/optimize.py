from dataclasses import dataclass
from typing import List, Optional

from input_data.load_customers import Customer
from input_data.load_vendors import Vendor
from ortools.linear_solver import pywraplp

from input_data.products import ProductSpec, ProductType
from optimize.constraints import set_constraints
from optimize.objective_function import create_objective_function
from optimize.variables import create_variables_and_set_on_solver

TERMINAL_COST = 10000
FULL_ORDER = 864
PRINT_VARIABLE_RESULTS = False


@dataclass(frozen=True)
class Action:
    volume_delivered: int
    order_nr: int
    customer_id: str
    vendor_id: Optional[str]
    delivery_number: Optional[int]
    product_type: ProductType
    internal_delivery: bool
    transportation_day: int


def start_optimize(
        vendors: List[Vendor],
        customers: List[Customer],
        product_specs: List[ProductSpec],
):
    solver = pywraplp.Solver(
        "SolveIntegerProblem", pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING
    )

    variables = create_variables_and_set_on_solver(
        vendors=vendors,
        customers=customers,
        solver=solver,
        product_specs=product_specs,
    )

    set_constraints(
        vendors=vendors,
        customers=customers,
        product_specs=product_specs,
        solver=solver,
        variables=variables,
    )

    objective = create_objective_function(
        solver=solver,
        variables=variables,
        vendors=vendors,
        customers=customers,
        product_specs=product_specs,
    )
    objective.SetMaximization()
    # solver.SetTimeLimit(60000)  # milli sec
    result_status = solver.Solve()
    _verify_solution(result_status, solver)

    if PRINT_VARIABLE_RESULTS:
        _print_solution_statistic(
            variables=variables,
            customers=customers,
            vendors=vendors,
            product_specs=product_specs,
            solver=solver,
        )

    actions = _get_actions(
        variables=variables,
        customers=customers,
        vendors=vendors,
        product_specs=product_specs,
    )
    return actions


def _verify_solution(result_status, solver):
    solution_is_verified = solver.VerifySolution(tolerance=0.001, log_errors=False)
    if result_status == pywraplp.Solver.OPTIMAL and solution_is_verified:
        if PRINT_VARIABLE_RESULTS:
            print("Optimal solution found.")
    else:
        if PRINT_VARIABLE_RESULTS:
            print("Optimal solution was not found.")
        if solution_is_verified:
            print("Using incumbent solution.")
        else:
            raise Exception("Could not find a feasible solution")


def _get_actions(
        variables,
        customers: List[Customer],
        vendors: List[Vendor],
        product_specs: List[ProductSpec],
):
    actions_in_house = [
        Action(
            volume_delivered=variables.x[v][d][c][o][p].solution_value(),
            order_nr=order.order_number,
            vendor_id=vendor.id,
            delivery_number=delivery.delivery_number,
            product_type=product.product_type,
            internal_delivery=True,
            customer_id=customer.id,
            transportation_day=order.departure_day
        )
        for v, vendor in enumerate(vendors)
        for d, delivery in enumerate(vendor.deliveries)
        for c, customer in enumerate(customers)
        for o, order in enumerate(customer.orders)
        for p, product in enumerate(product_specs)
        if variables.x[v][d][c][o][p].solution_value() > 0
    ]

    actions_from_competitors = [
        Action(
            volume_delivered=variables.y[c][o][p].solution_value(),
            order_nr=order.order_number,
            vendor_id=None,
            delivery_number=None,
            product_type=product.product_type,
            internal_delivery=False,
            customer_id=customer.id,
            transportation_day=order.departure_day
        )
        for c, customer in enumerate(customers)
        for o, order in enumerate(customer.orders)
        for p, product in enumerate(product_specs)
        if variables.y[c][o][p].solution_value() > 0
    ]
    all_actions = actions_in_house + actions_from_competitors
    return all_actions


def _print_solution_statistic(
    variables,
    customers,
    vendors,
    product_specs,
    solver,
):
    print("Objective value: " + str(solver.Objective().Value()))

    for v, vendor in enumerate(vendors):
        for d, delivery in enumerate(vendor.deliveries):
            for c, customer in enumerate(customers):
                for o, order in enumerate(customer.orders):
                    for p, product in enumerate(product_specs):
                        if variables.x[v][d][c][o][p].solution_value() > 0:
                            print("x(v" + str(v + 1) + "_d" + str(d + 1) + "_c" + str(c + 1) + "_o" + str(o + 1) + "_p" + str(p + 1) + "): " + str(variables.x[v][d][c][o][p].solution_value()))

    for c, customer in enumerate(customers):
        for o, order in enumerate(customer.orders):
            for p, product in enumerate(product_specs):
                if variables.y[c][o][p].solution_value() > 0:
                    print("y(c" + str(c + 1) + "_o" + str(o + 1) + "_p" + str(p + 1) + "): " + str(variables.y[c][o][p].solution_value()))

    # b_customer_index = 0
    # for c, customer in enumerate(customers):
    #     if customer.customer_category == CustomerCategory.B:
    #         for o, order in enumerate(customer.orders):
    #             for p, product in enumerate(product_specs):
    #                 if variables.t[b_customer_index][o][p].solution_value() > 0:
    #                     print("t(c" + str(c + 1) + "_o" + str(o + 1) + "_p" + str(p + 1) + "): " + str(variables.t[c][o][p].solution_value()))
    #         b_customer_index += 1

    # for v, vendor in enumerate(vendors):
    #     for d, delivery in enumerate(vendor.deliveries):
    #         for c, customer in enumerate(customers):
    #             for o, order in enumerate(customer.orders):
    #                 if variables.d[v][d][c][o].solution_value() > -10:
    #                     print("d(v" + str(v + 1) + "_d" + str(d + 1) + "_c" + str(c + 1) + "_o" + str(o + 1) + "): " + str(variables.d[v][d][c][o].solution_value()))
    #
    # for v, vendor in enumerate(vendors):
    #     for d, delivery in enumerate(vendor.deliveries):
    #         for c, customer in enumerate(customers):
    #             for o, order in enumerate(customer.orders):
    #                 if variables.o[v][d][c][o].solution_value() > -1:
    #                     print("o(v" + str(v + 1) + "_d" + str(d + 1) + "_c" + str(c + 1) + "_o" + str(o + 1) + "): " + str(variables.o[v][d][c][o].solution_value()))
