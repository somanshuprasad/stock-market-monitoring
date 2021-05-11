import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import sqlite3 as sl

class Sql():
    def init(self):
        self.conn = sl.connect('backend_database.db')
        self.cursor = self.conn.cursor()
    
    def _update_columns(self,table_name,col_list):
        # Query 1st row from a table, check if all columns in list exist or not
        existing_columns = list(pd.read_sql('SELECT * from Prices LIMIT 1',self.conn))
        missing = [col for col in col_list if col not in existing_columns]

        if len(missing) > 0:
            for col in missing:
                self.cursor.execute(f'ALTER TABLE {table_name} ADD COLUMN "{col}" FLOAT')



if __name__ == "__main__":
    from lib.online_interface import QueryIndicators

    t = QueryIndicators()

    t.get_data()

