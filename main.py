from lib.online_interface import QueryIndicators
from lib.db_interface import Sql
import time

# Initial Run
sql = Sql()
t = QueryIndicators()
t.get_data()
sql.insert_prices(t.prices)

for _ in range(20):
    t.get_data("price")
    sql.insert_prices(t.prices)