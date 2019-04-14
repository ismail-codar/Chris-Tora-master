from typing import List

from ortools.linear_solver.pywraplp import Variable

from input_data.customer_category import CustomerCategory
from input_data.load_customers import Customer
from input_data.load_vendors import Vendor
from input_data.products import ProductSpec, ProductType, Product
from optimize.variables import Variables


M = 1000000
QUANTITY_FULL_ORDER = 864


def set_constraints(
        vendors: List[Vendor],
        customers: List[Customer],
        product_specs: List[ProductSpec],
        solver,
        variables: Variables
):
    _set_supply_and_demand_constraints(
        y_vars=variables.y,
        x_vars=variables.x,
        vendors=vendors,
        product_specs=product_specs,
        customers=customers,
        solver=solver,
    )
    _set_a_customer_constraints(
        x_vars=variables.x,
        y_vars=variables.y,
        t_vars=variables.t,
        customers=customers,
        solver=solver,
        vendors=vendors,
        product_specs=product_specs,
    )
    _set_cross_docking_constraint(
        x_vars=variables.x,
        d_vars=variables.d,
        vendors=vendors,
        product_specs=product_specs,
        customers=customers,
        solver=solver,
    )
    _set_time_constraints(
        x_vars=variables.x,
        z_vars=variables.z,
        vendors=vendors,
        product_specs=product_specs,
        customers=customers,
        solver=solver,
    )


# Cross-Docking Constraint
def _set_cross_docking_constraint(
        x_vars: List[Variable],
        d_vars: List[Variable],
        vendors: List[Vendor],
        product_specs: List[ProductSpec],
        customers: List[Customer],
        solver,
):
    for v, vendor in enumerate(vendors):
        for d, delivery in enumerate(vendor.deliveries):
            for c, customer in enumerate(customers):
                for o, order in enumerate(customer.orders):

                    constraint_cross_docking = solver.Constraint(-solver.infinity(), QUANTITY_FULL_ORDER)
                    constraint_cross_docking.SetCoefficient(d_vars[o], -M)

                    for p, product in enumerate(product_specs):
                        constraint_cross_docking.SetCoefficient(x_vars[v][d][c][o][p], 1)


# Time Constraint
def _set_time_constraints(
   x_vars: List[Variable],
   z_vars: List[Variable],
   vendors: List[Vendor],
   product_specs: List[ProductSpec],
   customers: List[Customer],
   solver,
):
    # Cannot send fish that arrives after departure day
    for v, vendor in enumerate(vendors):
        for d, delivery in enumerate(vendor.deliveries):
            for c, customer in enumerate(customers):
                for o, order in enumerate(customer.orders):

                    constraint_time = solver.Constraint(-solver.infinity(), 0)
                    constraint_time.SetCoefficient(z_vars[v][d][c][o], -M)

                    for p, product in enumerate(product_specs):
                        constraint_time.SetCoefficient(x_vars[v][d][c][o][p], 1)

    for v, vendor in enumerate(vendors):
        for d, delivery in enumerate(vendor.deliveries):
            for c, customer in enumerate(customers):
                for o, order in enumerate(customer.orders):

                    constraint_time_pt2 = solver.Constraint(0, order.departure_day - delivery.delivery_day + M)
                    constraint_time_pt2.SetCoefficient(z_vars[v][d][c][o], M)


def _set_supply_and_demand_constraints(
        y_vars: List[Variable],
        x_vars: List[Variable],
        vendors: List[Vendor],
        product_specs: List[ProductSpec],
        customers: List[Customer],
        solver,
):
    # Cannot sell more than supply
    for v, vendor in enumerate(vendors):
        for d, delivery in enumerate(vendor.deliveries):
            for p, product in enumerate(product_specs):

                if _product_list_contains_product_p(product_type=product.product_type, products=delivery.products):
                    volume_for_delivery_for_product = _get_volume_for_product_p(
                        product_type=product.product_type,
                        product_list=delivery.products,
                    )
                else:
                    volume_for_delivery_for_product = 0

                constraint_delivery_and_product = solver.Constraint(0, volume_for_delivery_for_product)
                for c, customer in enumerate(customers):
                    for o, order in enumerate(customer.orders):
                        constraint_delivery_and_product.SetCoefficient(x_vars[v][d][c][o][p], 1)

    # Cannot sell more than demand
    for c, customer in enumerate(customers):
        for o, order in enumerate(customer.orders):
            for p, product in enumerate(product_specs):

                if _product_list_contains_product_p(product_type=product.product_type, products=order.demand):
                    quantity_demanded_for_product_type = _get_volume_for_product_p(
                        product_type=product.product_type,
                        product_list=order.demand,
                    )
                else:
                    quantity_demanded_for_product_type = 0

                constraint_demand_and_product = solver.Constraint(0, quantity_demanded_for_product_type)
                constraint_demand_and_product.SetCoefficient(y_vars[c][o][p], 1)

                for v, vendor in enumerate(vendors):
                    for d, delivery in enumerate(vendor.deliveries):
                        constraint_demand_and_product.SetCoefficient(x_vars[v][d][c][o][p], 1)


def _get_volume_for_product_p(product_type: ProductType, product_list: List[Product]):
    for product in product_list:
        if product.product_type == product_type:
            volume = product.volume
            return volume


def _product_list_contains_product_p(product_type: ProductType, products: List[Product]):
    for product in products:
        if product.product_type == product_type:
            return True
    return False


def _set_contract_customer_constraints(
        x_vars,
        y_vars,
        customers: List[Customer],
        solver,
        vendors: List[Vendor],
        product_specs: List[ProductSpec]
):
    for c_c, customer_c in enumerate(customers):
        if customer_c.customer_category == CustomerCategory.Contract:
            for o_c, order_c in enumerate(customer_c.orders):
                for p, product in enumerate(product_specs):

                    if _product_list_contains_product_p(
                        product_type=product.product_type,
                        products=order_c.demand
                    ):
                        demand = _get_volume_for_product_p(
                            product_type=product.product_type,
                            product_list=order_c.demand
                        )

                    else:
                        demand = 0

                    constraint_contract_customer = solver.Constraint(demand, solver.infinity())

                    constraint_contract_customer.SetCoefficient(y_vars[c_c][o_c][p], 1)

                    for v, vendor in enumerate(vendors):
                            for d, delivery in enumerate(vendor.deliveries):
                                constraint_contract_customer.SetCoefficient(x_vars[v][d][c_c][o_c][p], 1)


def _set_a_customer_constraints(
        x_vars,
        y_vars,
        t_vars,
        customers: List[Customer],
        solver,
        vendors: List[Vendor],
        product_specs: List[ProductSpec]
):
    for c_a, customer_a in enumerate(customers):
        if customer_a.customer_category == CustomerCategory.A:
            for o_a, order_a in enumerate(customer_a.orders):
                b_customer_index = 0
                for c_b, customer_b in enumerate(customers):
                    if customer_b.customer_category == CustomerCategory.B:
                        for o_b, order_b in enumerate(customer_b.orders):
                            if order_a.departure_day >= order_b.departure_day:
                                for p, product in enumerate(product_specs):

                                    if _product_list_contains_product_p(
                                        product_type=product.product_type,
                                        products=order_a.demand
                                    ):
                                        demand = _get_volume_for_product_p(
                                            product_type=product.product_type,
                                            product_list=order_a.demand,
                                        )
                                    else:
                                        demand = 0

                                    constraint_a_customer = solver.Constraint(demand - M, solver.infinity())

                                    constraint_a_customer.SetCoefficient(y_vars[c_a][o_a][p], 1)
                                    constraint_a_customer.SetCoefficient(t_vars[b_customer_index][o_b][p], M)

                                    for v, vendor in enumerate(vendors):
                                        for d, delivery in enumerate(vendor.deliveries):
                                            constraint_a_customer.SetCoefficient(x_vars[v][d][c_a][o_a][p], 1)

                        b_customer_index += 1

    b_customer_index = 0
    for c_b, customer_b in enumerate(customers):
        if customer_b.customer_category == CustomerCategory.B:
            for o_b, order_b in enumerate(customer_b.orders):
                for p, product in enumerate(product_specs):

                    constraint_b_customer = solver.Constraint(-solver.infinity(), 0)
                    constraint_b_customer.SetCoefficient(y_vars[c_b][o_b][p], 1)
                    constraint_b_customer.SetCoefficient(t_vars[b_customer_index][o_b][p], -M)

                    for v, vendor in enumerate(vendors):
                        for d, delivery in enumerate(vendor.deliveries):
                            constraint_b_customer.SetCoefficient(x_vars[v][d][c_b][o_b][p], 1)
            b_customer_index += 1






















