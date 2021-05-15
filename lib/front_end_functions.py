import pandas as pd
import sqlite3 as sl
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time

class Sql:
    def __init__(self):
        self.conn = sl.connect('backend_database.db')
        self.cursor = self.conn.cursor()

    def _safe_sql_call(self,query):
        # Receives a sql query, tries to call teh db. if the query fails, tries again after 1 second else returns
        self.conn = sl.connect('backend_database.db')
        for _ in range(10):
            try:
                df = pd.read_sql(query,self.conn)
                io_error = None
            except: pass

            if io_error:
                time.sleep(1)
            else: 
                return df

    def query_price_df(self):
        query = "SELECT * FROM Prices ORDER BY time DESC LIMIT 1"
        df = self._safe_sql_call(query).drop("time",axis=1).T.reset_index()
        df.columns = ["Ticker","Price"]
        return df
    
    def query_pivot_df(self):
        query = "SELECT * FROM Pivot"
        df = self._safe_sql_call(query).set_index("Ticker")
        return df
    
    def query_ma_df(self,):
        query = "SELECT * FROM MovAvg"
        df = self._safe_sql_call(query).set_index("Ticker")
        return df

    def query_all_prices_tday_df(self):
        query = "SELECT * FROM Prices WHERE time > (SELECT DATETIME('now', '-1 day'))"
        df = self._safe_sql_call(query)
        return df


class CreateDf():
    def _find_between(self,s):
        # Takes a series of pivot data. Identifies which technical indicators the price is currently in between (S1,S2,...R2,R1)
        right = np.searchsorted(s[2:].to_numpy(),s["Price"],side="left")
        left = right-1
        right = right if right < len(s) - 2 else right-1
        return (s.index[left+2],s.index[right+2],s[2:][left],s[2:][right])

    def pivot(self):
        # Creates a table which contains the latest price along with all the pivot indicators. 
        self.sql = Sql()
        self.pivot_df = self.sql.query_pivot_df()
        self.price_df = self.sql.query_price_df().fillna(0) # fillna to ensure nans don't end up in the calculation

        combined = pd.merge(self.price_df,self.pivot_df,left_on="Ticker",right_index=True,how="outer")
        combined["func"] = combined.apply(self._find_between,axis=1)

        combined["tech_inbetween_lbl"] = combined["func"].apply(lambda row: row[0:2])
        combined["tech_inbetween_num"] = combined["func"].apply(lambda row: row[2:])
        combined["tech_inbetween_perc"] = combined.apply(lambda row: ((row["Price"]-row["tech_inbetween_num"][0])/(np.diff(row["tech_inbetween_num"])[0]+0.000001), (row["tech_inbetween_num"][1]-row["Price"])/(np.diff(row["tech_inbetween_num"])[0]+0.000001)),axis=1)
        combined["tech_inbetween_perc"] = combined["tech_inbetween_perc"].apply(lambda row: (f"{round(row[0]*100)}%", f"{round(row[1]*100)}%"))

        return combined[["Ticker","Price","tech_inbetween_lbl","tech_inbetween_num","tech_inbetween_perc"]].astype(str)

    def mov_avg(self):
        self.sql = Sql()
        self.price_df = self.sql.query_price_df().fillna(0) # fillna to ensure nans don't end up in the calculation
        self.ma_df = self.sql.query_ma_df()

        combined = pd.merge(self.price_df,self.ma_df,left_on="Ticker",right_index=True,how="outer")

        for col in [col for col in combined.columns if "MA" in col]:
            combined[f"{col} %"] = round(combined[col]/combined["Price"]*100, 2) # Calculate percentage difference between Moving average and Price

        return combined[[col for col in combined.columns if "%" in col or col in ["Ticker","Price"]] ]
    
    def all_prices_tday(self):
        # Queries the entire price list from SQL
        self.sql = Sql()
        all_prices_df = self.sql.query_all_prices_tday_df()
        ticker_list = [col for col in all_prices_df.columns if col != "time"]
        return all_prices_df,ticker_list
        

class CreatePlot():
    def pivot(self,ticker=None):
        self.sql = Sql()
        self.price_df = self.sql.query_all_prices_tday_df()
        self.pivot_df = self.sql.query_pivot_df()
        pivot_list = ["R3","R2","R1","Pivot Points","S1","S2","S3"]

        if ticker is None: ticker = self.price_df.columns[1]
        df = self.price_df[["time",ticker]].copy()

        for col in pivot_list:
            df[col] = self.pivot_df.loc[ticker][col]

        fig = px.line(df, x='time', y=ticker)
        for col in pivot_list:
            fig.add_trace(go.Scatter(x=df["time"],
                                    y=df[col],
                                    name=col,
                                    line={"width":2, "dash":'dash'}))
        return fig