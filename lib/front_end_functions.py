import pandas as pd
import sqlite3 as sl
import numpy as np

class Sql:
    def __init__(self):
        self.conn = sl.connect('backend_database.db')
        self.cursor = self.conn.cursor()


    def query_price_df(self):
        self.conn = sl.connect(r"C:\Users\soman\OneDrive\Desktop\Python Projects\Dad's projects\technicals-scraper\backend_database.db")
        # self.conn = sl.connect("backend_database.db")
        query = "SELECT * FROM Prices ORDER BY time DESC LIMIT 1"
        df = pd.read_sql(query,self.conn).drop("time",axis=1).T.reset_index()
        df.columns = ["Ticker","Price"]
        return df
    
    def query_pivot_df(self):
        self.conn = sl.connect(r"C:\Users\soman\OneDrive\Desktop\Python Projects\Dad's projects\technicals-scraper\backend_database.db")
        # self.conn = sl.connect("backend_database.db")
        query = "SELECT * FROM Pivot"
        df = pd.read_sql(query,self.conn).set_index("Ticker")
        return df
    
    def call_ma_df(self,):
        pass


class CreateDf():
    def __init__(self,*args):
        sql = Sql()
        if len(args) == 0: args=("pivot","ma")

        self.price_df = sql.query_price_df().fillna(0)
        if "pivot" in args: self.pivot_df = sql.query_pivot_df()
        if "ma" in args: self.ma_df = sql.call_ma_df()

    def _find_between(self,s):
        # Takes a series of pivot data. Identifies which technical indicators the price is currently in between (S1,S2,...R2,R1)
        right = np.searchsorted(s[2:].to_numpy(),s["Price"],side="left")
        left = right-1
        right = right if right < len(s) - 2 else right-1
        return (s.index[left+2],s.index[right+2],s[2:][left],s[2:][right])

    def pivot(self):
        combined = pd.merge(self.price_df,self.pivot_df,left_on="Ticker",right_index=True,how="outer")
        combined["func"] = combined.apply(self._find_between,axis=1)

        combined["tech_inbetween_lbl"] = combined["func"].apply(lambda row: row[0:2])
        combined["tech_inbetween_num"] = combined["func"].apply(lambda row: row[2:])
        combined["tech_inbetween_perc"] = combined.apply(lambda row: ((row["Price"]-row["tech_inbetween_num"][0])/(np.diff(row["tech_inbetween_num"])[0]+0.000001), (row["tech_inbetween_num"][1]-row["Price"])/(np.diff(row["tech_inbetween_num"])[0]+0.000001)),axis=1)
        combined["tech_inbetween_perc"] = combined["tech_inbetween_perc"].apply(lambda row: (f"{round(row[0]*100)}%", f"{round(row[1]*100)}%"))


        return combined[["Ticker","Price","tech_inbetween_lbl","tech_inbetween_num","tech_inbetween_perc"]].astype(str)