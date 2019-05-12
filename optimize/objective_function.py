import math
from typing import List

from helpers import order_has_product_p, get_transport_price_for_customer_c, get_price_for_product_p, \
    get_extra_purchase_price_for_product_p, delivery_has_product_p
from input_data.load_customers import Customer
from input_data.load_vendors import Vendor
from input_data.products import ProductSpec
from optimize.variables import Variables


def create_objective_function(
        vendors: List[Vendor],
        customers: List[Customer],
        solver,
        variables: Variables,
        product_specs: List[ProductSpec],
        number_of_scenarios: int,
        number_of_days_in_one_run: int,
):
    objective = solver.Objective()

    _set_x_objective(
        x_vars=variables.x,
        customers=customers,
        vendors=vendors,
        product_specs=product_specs,
        objective=objective,
        number_of_scenarios=number_of_scenarios,
        number_of_days_in_one_run=number_of_days_in_one_run,
    )

    _set_y_objective(
        y_vars=variables.y,
        customers=customers,
        product_specs=product_specs,
        objective=objective,
        number_of_scenarios=number_of_scenarios,
        number_of_days_in_one_run=number_of_days_in_one_run,
    )

    _set_o_objective(
        customers=customers,
        vendors=vendors,
        o_vars=variables.o,
        objective=objective,
        number_of_scenarios=number_of_scenarios,
        number_of_days_in_one_run=number_of_days_in_one_run,
    )

    return objective


def _set_x_objective(
        x_vars,
        customers: List[Customer],
        vendors: List[Vendor],
        product_specs: List[ProductSpec],
        objective,
        number_of_scenarios: int,
        number_of_days_in_one_run: int,
):
    for s in range(number_of_scenarios):
        for v, vendor in enumerate(vendors):
            for d, delivery in enumerate(vendor.deliveries):
                for c, customer in enumerate(customers):
                    for o, order in enumerate(customer.orders):
                        for p, product_spec in enumerate(product_specs):
                            if order_has_product_p(product_type=product_spec.product_type, products=order.demand) \
                                    and delivery_has_product_p(product_type=product_spec.product_type, products=order.demand):

                                sales_price = get_price_for_product_p(product_type=product_spec.product_type, products=order.demand)
                                transport_cost = get_transport_price_for_customer_c(
                                    product_type=product_spec.product_type,
                                    transportation_price_per_box=customer.transportation_price_per_box,
                                    customer_id=customer.id
                                )
                                probability = _get_probability_of_scenario(
                                    scenario_index=s,
                                    number_of_scenarios=number_of_scenarios,
                                    number_of_days_in_one_run=number_of_days_in_one_run,
                                )
                                if customer.out_of_country:
                                    customs_cost = product_spec.customs_cost
                                    coefficient = sales_price - transport_cost - customs_cost
                                else:
                                    coefficient = sales_price - transport_cost

                                objective.SetCoefficient(x_vars[s][v][d][c][o][p], coefficient * probability)


def _set_y_objective(y_vars, customers: List[Customer], product_specs: List[ProductSpec], objective, number_of_scenarios: int, number_of_days_in_one_run: int):
    for s in range(number_of_scenarios):
        for c, customer in enumerate(customers):
            for o, order in enumerate(customer.orders):
                for p, product_spec in enumerate(product_specs):
                    if order_has_product_p(product_type=product_spec.product_type, products=order.demand):

                        transport_price = get_transport_price_for_customer_c(
                            product_type=product_spec.product_type,
                            transportation_price_per_box=customer.transportation_price_per_box,
                            customer_id=customer.id
                        )
                        price = get_price_for_product_p(product_type=product_spec.product_type, products=order.demand)
                        extra_cost = get_extra_purchase_price_for_product_p(
                            product_type=product_spec.product_type,
                            product_specs=product_specs
                        )
                        if customer.out_of_country:
                            customs_cost = product_spec.customs_cost
                            coefficient = price - transport_price - extra_cost - customs_cost
                        else:
                            coefficient = price - transport_price - extra_cost

                        probability = _get_probability_of_scenario(
                            scenario_index=s,
                            number_of_scenarios=number_of_scenarios,
                            number_of_days_in_one_run=number_of_days_in_one_run,
                        )

                        objective.SetCoefficient(y_vars[s][c][o][p], coefficient * probability)


# Oslo cost
def _set_o_objective(customers, vendors, o_vars, objective, number_of_scenarios: int, number_of_days_in_one_run: int):
    for s in range(number_of_scenarios):
        for v, vendor in enumerate(vendors):
            for d, delivery in enumerate(vendor.deliveries):
                for c, customer in enumerate(customers):
                    for o, order in enumerate(customer.orders):
                        probability = _get_probability_of_scenario(
                            scenario_index=s,
                            number_of_scenarios=number_of_scenarios,
                            number_of_days_in_one_run=number_of_days_in_one_run,
                        )
                        objective.SetCoefficient(o_vars[s][v][d][c][o], -1 * probability)


def _get_probability_of_scenario(
        scenario_index: int,
        number_of_scenarios: int,
        number_of_days_in_one_run: int,
):
    if number_of_scenarios == 1:
        return 1
    else:
        probability = 1

        for day_index in range(number_of_days_in_one_run):
            supply_level = _get_supply_level_from_scenario_index(
                arrival_day=day_index,
                number_of_days_in_one_run=number_of_days_in_one_run,
                scenario_index=scenario_index,
                start_day=0,
            )
            if supply_level == 0:
                probability *= 0.20
            if supply_level == 1:
                probability *= 0.60
            if supply_level == 2:
                probability *= 0.20
        return probability


def _get_supply_level_from_scenario_index(arrival_day, number_of_days_in_one_run, scenario_index, start_day):
    day_index_of_this_delivery = arrival_day - start_day
    last_day_index = number_of_days_in_one_run - 1
    days_to_iterate_back_in_scenario_tree = last_day_index - day_index_of_this_delivery

    if days_to_iterate_back_in_scenario_tree > 0:
        branch_index_of_the_day_of_the_delivery = math.floor(
            scenario_index / (3 ** days_to_iterate_back_in_scenario_tree))
    else:
        branch_index_of_the_day_of_the_delivery = scenario_index
    supply_level = branch_index_of_the_day_of_the_delivery % 3
    return supply_level
