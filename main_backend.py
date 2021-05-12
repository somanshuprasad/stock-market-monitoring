from pandas.core.indexing import is_nested_tuple
from lib.online_interface import QueryIndicators
from lib.db_interface import Sql
import time

def get_all_data():
    t.get_data() # choices: "price","pivot","ma"
    sql.insert_prices(t.prices)
    sql.insert_pivot(t.technicals)
    sql.insert_moving_average(t.technicals)

def get_price_data():
    t.get_data("price") # choices: "price","pivot","ma"
    sql.insert_prices(t.prices)

if __name__ == "__main__":
    # create web and sql interface objects
    sql = Sql()
    t = QueryIndicators()

    # Initial Run
    get_all_data()
    start = time.perf_counter()
    
    while True:
        is_technical_run = False

        if time.perf_counter() - start >= 3600:
            get_all_data()
            is_technical_run = True
        else:
            get_price_data()

        if is_technical_run: start = time.perf_counter()