import requests
from requests.packages.urllib3.util import Retry
from requests.adapters import HTTPAdapter
from requests import Session

import pandas as pd
from bs4 import BeautifulSoup
import sqlite3 as sl
import sys

class QueryIndicators():
    
    def __init__(self):
        self._get_ticker_list()
        
        # setting up a sessions object with headers and retries
        self.s = Session()
        self.s.mount('https://', HTTPAdapter(max_retries=Retry(total=5,backoff_factor=1)))
        self.s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"})
    
    def _get_ticker_list(self):
        self.ticker_json = {}
        
        self.ticker_json["equities"] = list(pd.read_csv("equity_tickers.csv")["url_name"])
        self.ticker_json["indices"] = list(pd.read_csv("indices_tickers.csv")["url_name"])
        self.ticker_json["currencies"] = list(pd.read_csv("currency_tickers.csv")["url_name"])

    def _request(self,ticker,asset,time_frame=3600):
        base_url = f"https://in.investing.com/{asset}/"
        
        try:
            response = self.s.get(f"{base_url}{ticker}-technical?timeFrame={time_frame}",timeout=5)
        except KeyboardInterrupt: # incase I want to stop program in between a requests run
            sys.exit()
        except:
            response = False

        return response

    def get_data(self,*args,**kwargs):
        if len(args) == 0: args = ("price","pivot","ma") # if no arguments are specified, default to all
        time_frame = kwargs.get("time_frame",3600) # default time frame to 3600 sec/1 hour if not specified

        self.prices = {}
        self.technicals = {"ma":{},"pivot":{}}
        self.error_tickers = []

        # looping through asset classes
        for asset,ticker_list in self.ticker_json.items():
            #looping through each ticker per asset class 
            for ticker in ticker_list:
                response = self._request(ticker,asset,time_frame=time_frame)
                
                # Add to error_tickers incase of issues
                if response:
                    pass
                else:
                    self.error_tickers.append(ticker)
                    continue

                soup = BeautifulSoup(response.text, "html5lib")

                if "price" in args:
                    self.prices[ticker] = float(soup.find("bdo", {"class": "last-price-value js-streamable-element"}).text.replace(",",""))
                
                if "pivot" in args:
                    for df in pd.read_html(response.text):
                        if "Pivot Points" in df.columns:
                            df = df.T
                            df.columns = df.iloc[0]
                            self.technicals["pivot"][ticker] = df.drop(df.index[0])["Classic"]
                
                if "ma" in args:
                    for df in pd.read_html(response.text):
                        if "Period" in df.columns and "Exponential" in df.columns:
                            s = df.set_index("Period")["Simple"].str.split(" ",expand=True)[0].copy()
                            self.technicals["ma"][ticker] = s.fillna(0).astype(float)

class DbInterface():
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
    t = QueryIndicators()

    t.get_data()

    for technical,tickers in t.technicals.items():
        for ticker,df in tickers.items():
            print(ticker,df)

