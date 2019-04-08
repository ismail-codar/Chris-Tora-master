from input_data.load_customers import load_customers
from input_data.load_vendors import load_vendors
from input_data.products import load_product_spec
from optimize.optimize import start_optimize


def start_run():
    vendors = load_vendors()
    customers = load_customers()
    product_specs = load_product_spec()

    start_optimize(
        vendors=vendors,
        customers=customers,
        product_specs=product_specs
    )


start_run()
