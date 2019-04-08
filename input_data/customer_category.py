from enum import Enum


class CustomerCategory(Enum):
    Contract = 0
    A = 1
    B = 2


def get_customer_category(customer_category: str) -> CustomerCategory:
    if customer_category == "a":
        return CustomerCategory.A
    if customer_category == "b":
        return CustomerCategory.B
    if customer_category == "contract":
        return CustomerCategory.Contract
    else:
        raise Exception("unknown customer category")
