from input_data.load_customers import load_customers
from input_data.load_vendors import load_vendors
from input_data.products import load_product_spec
from optimize.optimize import start_optimize
from profit import calculate_profit_for_current_start_day
from scenarios.load_scenarios import load_scenarios

from simulation.start_simulation import _filter_out_deliveries_after_end_time, \
    _filter_out_order_out_of_time_scope, run_simulation
from solution_method import SolutionMethod


SIMULATE_RESULTS = True
NUMBER_OF_SCENARIOS = 10
START_DAY = 1
END_DAY = 15
ADJUST_DELIVERY_ESTIMATE = 0 # Percent, 0 % -> no change


def start_run():

    for test_index in range(3):
        if test_index == 0:
            NUMBER_OF_DAYS_IN_EACH_RUN = 3
            SOLUTION_METHOD = SolutionMethod.STOCHASTIC
            ONE_PRODUCT_TYPE_AT_THE_TIME = True

        elif test_index == 1:
            NUMBER_OF_DAYS_IN_EACH_RUN = 2
            SOLUTION_METHOD = SolutionMethod.STOCHASTIC
            ONE_PRODUCT_TYPE_AT_THE_TIME = True

        else:
            NUMBER_OF_DAYS_IN_EACH_RUN = 5
            SOLUTION_METHOD = SolutionMethod.DETERMINISTIC
            ONE_PRODUCT_TYPE_AT_THE_TIME = False

        if SOLUTION_METHOD == SolutionMethod.STOCHASTIC and not ONE_PRODUCT_TYPE_AT_THE_TIME:
            raise Exception("If you do a stochastic run, you can only do one product type at the time")

        customers = load_customers()
        product_specs = load_product_spec()

        if SIMULATE_RESULTS:
            scenarios = load_scenarios(number_of_scenarios=NUMBER_OF_SCENARIOS)
            number_of_runs_in_one_scenario = (END_DAY - START_DAY) - NUMBER_OF_DAYS_IN_EACH_RUN + 2

            run_simulation(
                customers=customers,
                number_of_runs_in_one_scenario=number_of_runs_in_one_scenario,
                product_specs=product_specs,
                scenarios=scenarios,
                start_day=START_DAY,
                number_of_days_in_each_run=NUMBER_OF_DAYS_IN_EACH_RUN,
                solution_method=SOLUTION_METHOD,
                one_product_type_at_the_time=ONE_PRODUCT_TYPE_AT_THE_TIME,
                adjust_delivery_estimate=ADJUST_DELIVERY_ESTIMATE,
                end_day=END_DAY,
            )

        else:
            vendors = load_vendors(
                path="input_data/deliveries.xlsx",
                adjust_delivery_estimate=ADJUST_DELIVERY_ESTIMATE,
            )
            start_day = START_DAY
            end_day = start_day + NUMBER_OF_DAYS_IN_EACH_RUN
            vendors_with_relevant_deliveries = _filter_out_deliveries_after_end_time(
                vendors=vendors,
                end_day=end_day,
            )
            customers_with_relevant_orders = _filter_out_order_out_of_time_scope(
                customers=customers,
                start_day=start_day,
                end_day=end_day,
            )
            actions = start_optimize(
                vendors=vendors_with_relevant_deliveries,
                customers=customers_with_relevant_orders,
                product_specs=product_specs,
                solution_method=SOLUTION_METHOD,
                number_of_days_in_each_run=NUMBER_OF_DAYS_IN_EACH_RUN,
                start_day=start_day,
            )
            actions_with_transportation_date_today = [
                action
                for action in actions
                if action.transportation_day == start_day
            ]
            profit_for_start_day = calculate_profit_for_current_start_day(
                vendors=vendors_with_relevant_deliveries,
                customers=customers_with_relevant_orders,
                product_specs=product_specs,
                todays_actions=actions_with_transportation_date_today,
            )
            print("Profit for start day: " + str(profit_for_start_day))


start_run()
