import pandas as pd
import datetime
import sqlite3 as sl

class Sql():
    def __init__(self):
        self.conn = sl.connect('backend_database.db')
        self.cursor = self.conn.cursor()
    
    def _update_columns(self,table_name,col_list):
        # Query 1st row from a table, check if all columns in list exist or not
        existing_columns = list(pd.read_sql(f'SELECT * from {table_name} LIMIT 1',self.conn))
        missing = [col for col in col_list if col not in existing_columns]

        if len(missing) > 0:
            for col in missing:
                self.cursor.execute(f'ALTER TABLE {table_name} ADD COLUMN "{col}" FLOAT')
                self.conn.commit()

    def insert_prices(self,records):
        columns = ("time",) + tuple([col for col in records.keys()])
        data = (datetime.datetime.now(),) + tuple([price for _,price in records.items()])
        values = ",".join(["?"] * len(data))
        
        self._update_columns("Prices",columns)
        
        query = (f'INSERT into Prices {columns} VALUES ({values})') # format: INSERT into Prices ('time', 'ticker1', 'ticker2', 'ticker3', 'ticker4') VALUES (?,?,?,?,?)
        self.cursor.execute(query, data)
        self.conn.commit()
    
    def insert_technicals(self,technicals):
        pass



if __name__ == "__main__":
    from lib.online_interface import QueryIndicators

    # Initial Run
    t = QueryIndicators()
    t.get_data()


