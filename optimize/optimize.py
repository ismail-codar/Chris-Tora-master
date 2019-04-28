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


@dataclass(frozen=True)
class RealizedResult:
    volume_delivered: int
    order_nr: str
    customer_id: str
    vendor_id: Optional[str]
    delivery_id: Optional[int]
    product_type: ProductType
    internal_delivery: bool


def start_optimize(
        vendors: List[Vendor],
        customers: List[Customer],
        product_specs: List[ProductSpec],
        start_day: int,
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
    _print_solution_statistic(
        variables=variables,
        customers=customers,
        vendors=vendors,
        product_specs=product_specs,
        solver=solver,
    )
    realized_results = _get_realized_result(
        variables=variables,
        start_day=start_day,
        customers=customers,
        vendors=vendors,
        product_specs=product_specs,
    )
    return realized_results


def _verify_solution(result_status, solver):
    solution_is_verified = solver.VerifySolution(tolerance=0.001, log_errors=False)
    if result_status == pywraplp.Solver.OPTIMAL and solution_is_verified:
        print("Optimal solution found.")
    else:
        print("Optimal solution was not found.")
        if solution_is_verified:
            print("Using incumbent solution.")
        else:
            raise Exception("Could not find a feasible solution")


def _get_realized_result(
        variables,
        start_day,
        customers,
        vendors,
        product_specs,
):
    realized_results = []
    for v, vendor in enumerate(vendors):
        for d, delivery in enumerate(vendor.deliveries):
            for c, customer in enumerate(customers):
                for o, order in enumerate(customer.orders):
                    for p, product in enumerate(product_specs):
                        if variables.x[v][d][c][o][p].solution_value() > 0 and order.departure_day == start_day:
                            realized_result = RealizedResult(
                                volume_delivered=variables.x[v][d][c][o][p].solution_value(),
                                order_nr=order.order_number,
                                vendor_id=vendor.id,
                                delivery_id=delivery.id,
                                product_type=product.product_type,
                                internal_delivery=True,
                                customer_id=customer.id,
                            )
                            realized_results.append(realized_result)

    for c, customer in enumerate(customers):
        for o, order in enumerate(customer.orders):
            for p, product in enumerate(product_specs):
                if variables.y[c][o][p].solution_value() > 0 and order.departure_day == start_day:
                    realized_result = RealizedResult(
                        volume_delivered=variables.x[v][d][c][o][p].solution_value(),
                        order_nr=order.order_number,
                        vendor_id=None,
                        delivery_id=None,
                        product_type=product.product_type,
                        internal_delivery=False,
                        customer_id=customer.id,
                    )
                    realized_results.append(realized_result)
    return realized_results


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

    for v, vendor in enumerate(vendors):
        for d, delivery in enumerate(vendor.deliveries):
            for c, customer in enumerate(customers):
                for o, order in enumerate(customer.orders):
                    if variables.d[v][d][c][o].solution_value() > -10:
                        print("d(v" + str(v + 1) + "_d" + str(d + 1) + "_c" + str(c + 1) + "_o" + str(o + 1) + "): " + str(variables.d[v][d][c][o].solution_value()))

    for v, vendor in enumerate(vendors):
        for d, delivery in enumerate(vendor.deliveries):
            for c, customer in enumerate(customers):
                for o, order in enumerate(customer.orders):
                    if variables.o[v][d][c][o].solution_value() > -1:
                        print("o(v" + str(v + 1) + "_d" + str(d + 1) + "_c" + str(c + 1) + "_o" + str(o + 1) + "): " + str(variables.o[v][d][c][o].solution_value()))
