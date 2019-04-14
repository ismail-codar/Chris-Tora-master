from typing import List
from input_data.load_customers import Customer, TransportationCost
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
    _set_transportation_to_customer_objective(
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


def _set_transportation_to_customer_objective(customers, product_specs, vendors, objective, x_vars, y_vars):
    for c, customer in enumerate(customers):
        for p, product in enumerate(product_specs):

            transport_price = _get_transport_price_for_customer_c(
                product_type=product.product_type,
                transportation_price_per_box=customer.transportation_price_per_box,
            )
            for o, order in enumerate(customer.orders):
                objective.SetCoefficient(y_vars[c][o][p], - transport_price)

                for v, vendor in enumerate(vendors):
                    for d, delivery in enumerate(vendor.deliveries):
                        objective.SetCoefficient(x_vars[v][d][c][o][p], - transport_price)


def _get_transport_price_for_customer_c(product_type: ProductType, transportation_price_per_box: List[TransportationCost]):
    for transportation_price in transportation_price_per_box:
        if transportation_price.product_type == product_type:
            return transportation_price.cost


def _set_purchase_cost_extra_purchase_objective(customers, product_specs: List[ProductSpec], objective, y_vars):
    for p, product in enumerate (product_specs):
        extra_price = _get_extra_purchase_price_for_product_p(product_type=product.product_type, product_specs=product_specs)
        for c, customer in enumerate(customers):
            for o, order in enumerate(customer.orders):
                objective.SetCoefficient(y_vars[c][o][p], - extra_price)


def _get_extra_purchase_price_for_product_p(product_type: ProductType, product_specs: List[ProductSpec]):
    for product_spec in product_specs:
        if product_spec.product_type == product_type:
            extra_price = product_spec.extra_cost
            return extra_price
