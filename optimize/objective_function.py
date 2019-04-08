from typing import List
from input_data.load_customers import Customer
from input_data.load_vendors import Vendor
from input_data.products import ProductSpec, ProductType, Product
from optimize.variables import Variables


def create_objective_function(
        vendors: List[Vendor],
        customers: List[Customer],
        solver,
        variables: Variables,
        product_specs: List[ProductSpec]
):
    objective = solver.Objective()

    _set_revenue_objective(
        customers=customers,
        product_specs=product_specs,
        vendors=vendors,
        objective=objective,
        x_vars=variables.x,
        y_vars=variables.y,
    )

    return objective


def _set_revenue_objective(customers, product_specs, vendors, objective, x_vars, y_vars):
    for c, customer in enumerate(customers):
        for o, order in enumerate(customer.orders):
            for p, product in enumerate(product_specs):

                if _order_has_product_p(product_type=product.product_type, products=order.demand):
                    price = _get_price_for_product_p(product_type=product.product_type, products=order.demand)
                    objective.SetCoefficient(y_vars[c][o][p], price)

                    for v, vendor in enumerate(vendors):
                        for d, delivery in enumerate(vendor.deliveries):
                            objective.SetCoefficient(x_vars[v][d][c][o][p], price)


def _get_price_for_product_p(product_type: ProductType, products: List[Product]):
    for product in products:
        if product.product_type == product_type:
            price = product.price
            return price


def _order_has_product_p(product_type: ProductType, products: List[Product]):
    for product in products:
        if product.product_type == product_type:
            return True
    return False
