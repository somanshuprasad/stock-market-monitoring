import requests
import pandas as pd

class TechnicalAnalysis():
    
    def __init__(self):
        pass
    
    def get_ticker_list(self):
        self.ticker_json = {}
        
        with open("stock_list.txt","r") as f: self.ticker_json["equities"] = f.read().split(",")
        with open("index_list.txt","r") as f: self.ticker_json["indices"] = f.read().split(",")
    
    def get_technicals(self):
        head = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"}
        self.technicals_df={}
        self.error_tickers = []
        
        # looping through asset classes
        for asset,ticker_list in self.ticker_json.items():
            base_url = f"https://in.investing.com/{asset}/"

            #looping through each ticker per asset class 
            for ticker in ticker_list:
                response = requests.get(f"{base_url}{ticker}-technical",headers=head)
                if response:
                    for df in pd.read_html(response.text):
                        if "Pivot Points" in df.columns:
                            self.technicals_df[ticker] = df
                else: self.error_tickers.append(ticker)
    


if __name__ == "__main__":
    t = TechnicalAnalysis()

    t.get_ticker_list()
    t.get_technicals()

    for ticker,df in t.technicals_df.items():
        print(ticker,df)

