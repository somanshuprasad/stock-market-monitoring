import pandas as pd
import datetime
import sqlite3 as sl

class Sql():
    def __init__(self):
        self.conn = sl.connect('backend_database.db')
        self.cursor = self.conn.cursor()
    
    def _create_new_db(self):
        # to be used incase something goes wrong with existing db and new one needs to be created
        new_table = {"Prices" : ["time TIMESTAMP"],
                     "Pivot" : ['Ticker TEXT PRIMARY KEY', 'S3 FLOAT', 'S2 FLOAT', 'S1 FLOAT', '"Pivot Points" FLOAT', 'R1 FLOAT', 'R2 FLOAT', 'R3 FLOAT'],
                     "MovAvg" : ['Ticker TEXT PRIMARY KEY', 'MA5 FLOAT', 'MA10 FLOAT', 'MA20 FLOAT', 'MA50 FLOAT', 'MA100 FLOAT', 'MA200 FLOAT']}
        
        for table_name,table_cols in new_table.items():
            delete_query = f"DROP TABLE {table_name}"
            create_query = f'CREATE TABLE {table_name} ({",".join(table_cols)})'
            
            self.cursor.execute(delete_query)
            self.cursor.execute(create_query)
            self.conn.commit()
        print("Database Cleared")            

    
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
    
    def insert_moving_average(self,technicals):
        # Loop thorugh each ticker in the technicals json and update the corresponding row value in Pivot Table
        for ticker in technicals["ma"]:
            columns = ('Ticker', 'MA5', 'MA10', 'MA20', 'MA50', 'MA100', 'MA200')
            data = (ticker,) + tuple(technicals["ma"][ticker])
            values = ",".join(["?"] * len(data))

            query = (f'INSERT OR REPLACE INTO MovAvg {columns} VALUES ({values})')
            self.cursor.execute(query, data)
            self.conn.commit()

    def insert_pivot(self,technicals):
        # Loop thorugh each ticker in the technicals json and update the corresponding row value in Moving Average Table 
        for ticker in technicals["pivot"]:
            columns = ('Ticker', 'S3', 'S2', 'S1', "Pivot Points", 'R1', 'R2', 'R3')
            data = (ticker,) + tuple(technicals["pivot"][ticker])
            values = ",".join(["?"] * len(data))

            query = (f'INSERT OR REPLACE INTO Pivot {columns} VALUES ({values})')
            self.cursor.execute(query, data)
            self.conn.commit()


if __name__ == "__main__":
    from lib.online_interface import QueryIndicators

    # Initial Run
    t = QueryIndicators()
    t.get_data()


