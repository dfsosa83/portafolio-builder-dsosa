# -*- coding: utf-8 -*-
"""
Created on Tue Mar 18 13:36:46 2025

@author: rblasser
"""



from utils.utility import Utility as util
from utils.data_fetcher import DataFetcher as fetch


stock = 'AAOI'
years = 5

df2 = fetch.get_prices(stock,years)


util.popup_graphly(stock,years,df2,'Returns')



df2['Date'] = df2.index

df2['LastDate'] = df2.apply(lambda x: df2[df2['Date'].dt.to_period('M') == x['Date'].to_period('M')]['Date'].max(), axis=1)
df2['isLastDate'] = df2['Date'] == df2['LastDate']






from utils.db_manager import PortfolioDB

db = PortfolioDB()






import yfinance as yf
from datetime import datetime, timedelta
from utils.data_fetcher import DataFetcher as fetch
import pandas as pd

query = "bladex"

res1 = fetch.search_stocks(query)

d1 = []
for each_res in res1:
    print(each_res['value'])
    d1.append(each_res['value'])


df1 = pd.DataFrame.from_dict(d1, orient='columns')



# Create a Ticker object for a specific stock symbol
query = 'VOO'
ticker = yf.Ticker(query)
years = 5
end = datetime.today().strftime('%Y-%m-%d')
start = (datetime.today() - timedelta(days=years*365)).strftime('%Y-%m-%d')


d1 = ticker.history(start=start, end=end, interval='1d')


news = ticker.get_news()

print(ticker.get_news())

# Access company information
info = ticker.info

# Print some key details
print("Company Name:", info.get('longName', 'N/A'))
print("Sector:", info.get('sector', 'N/A'))
print("Market Cap:", info.get('marketCap', 'N/A'))
print("Number of Employees:", info.get('fullTimeEmployees', 'N/A'))



# 3MSE.DE - Leverage Shares 3x Microsoft ETC

### METRICS TEST

from utils.metrics import StockMetrics as metrics


metric = metrics()

query = '3MSE.DE'

df1 = pd.DataFrame.from_dict(metric.get_stock_metrics(query), 
                             orient='index').reset_index()

df1.T.iloc[0]

d1 = pd.DataFrame(columns=df1.T.iloc[0])
d1.insert(pd.DataFrame(df1.T.iloc[1]))











