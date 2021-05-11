import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

class QueryIndicators():
    
    def __init__(self):
        self._get_ticker_list()
    
    def _get_ticker_list(self):
        df = pd.read_csv("investing_ticker.csv")
        self.ticker_json = {}
        
        self.ticker_json["equities"] = list(df["equities"])
        self.ticker_json["indices"] = list(df["indices"])

    def _request(self,ticker,asset,time_frame=3600):
        head = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"}
        base_url = f"https://in.investing.com/{asset}/"
        response = requests.get(f"{base_url}{ticker}-technical?timeFrame={time_frame}",headers=head)

        return response, datetime.now()

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
                response,req_time = self._request(ticker,asset,time_frame=time_frame)
                soup = BeautifulSoup(response.text, "html5lib")
                
                # Add to error_tickers incase of issues
                if response.status_code != 200:
                    self.error_tickers.append(ticker)
                    break

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
                            self.technicals["ma"][ticker] = df    



if __name__ == "__main__":
    t = QueryIndicators()

    t.get_data()

    for technical,tickers in t.technicals.items():
        for ticker,df in tickers.items():
            print(ticker,df)

