from lib.online_interface import QueryIndicators
from lib.db_interface import Sql
import datetime
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
    print("started running backend")
    sql = Sql()
    t = QueryIndicators()

    # Initial Run
    get_all_data()
    start = time.perf_counter()
    
    while True:
        is_technical_run = False

        if time.perf_counter() - start >= 10 * 60: # Run the technicals every 10 mins
            get_all_data()
            is_technical_run = True
            print(f"{datetime.datetime.now()}: techincals just ran. sample {t.technicals['ma']['reliance-industries']}")
        else:
            get_price_data()

        if len(t.error_tickers) > 0: print(f"following tickers had errors: {t.error_tickers}")

        if is_technical_run: start = time.perf_counter()

        