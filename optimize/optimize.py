from typing import List

from input_data.customer_category import CustomerCategory
from input_data.load_customers import Customer
from input_data.load_vendors import Vendor
from ortools.linear_solver import pywraplp

from input_data.products import ProductSpec
from optimize.constraints import set_constraints
from optimize.objective_function import create_objective_function
from optimize.variables import create_variables_and_set_on_solver

TERMINAL_COST = 10000
FULL_ORDER = 864


def start_optimize(
        vendors: List[Vendor],
        customers: List[Customer],
        product_specs: List[ProductSpec]
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

    for c, customer in enumerate(customers):
        for o, order in enumerate(customer.orders):
            if variables.d[c][o].solution_value() > 0:
                print("d(c" + str(c + 1) + "_o" + str(o + 1) + "): " + str(variables.d[c][o].solution_value()))

    for c, customer in enumerate(customers):
        for o, order in enumerate(customer.orders):
            if variables.o[c][o].solution_value() > 0:
                print("o(c" + str(c + 1) + "_o" + str(o + 1) + "): " + str(variables.o[c][o].solution_value()))