# -*- coding: utf-8 -*-
"""
Created on Tue Mar 18 09:56:22 2025

@author: rblasser
"""

import yfinance as yf
import requests
from datetime import datetime, timedelta


class DataFetcher:
    
    def search_stocks(query):
        if not query or len(query) < 2:
            return []
            
        try:
            url = f"https://query1.finance.yahoo.com/v1/finance/search?q={query}&quotesCount=20&newsCount=0&enableFuzzyQuery=false"
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers)
            data = response.json()
            
            suggestions = []
            if 'quotes' in data:
                for quote in data['quotes']:
                    if 'symbol' in quote and 'longname' in quote:
                        symbol = quote['symbol']
                        name = quote['longname']
                        if not any(x in symbol for x in ['-', '^', '=']) and isinstance(symbol, str) and isinstance(name, str):
                            suggestions.append({
                                "label": f"{symbol} - {name}",
                                "value": {"symbol": symbol, "name": name}
                            })
            return suggestions
        except Exception as e:
            print(f"Error searching stocks: {str(e)}")
            return []
    
    
    def get_stock_info(symbol):
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            return {
                'name': info.get('longName', ''),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'country': info.get('country', '')
            }
        except Exception as e:
            print(f"Error fetching info for {symbol}: {str(e)}")
            return None 
        
    
    def get_prices(symbol, years):
        
        end = datetime.today().strftime('%Y-%m-%d')
        start = (datetime.today() - timedelta(days=years*365)).strftime('%Y-%m-%d')
        
        ticker = yf.Ticker(symbol)
        
        if isinstance(ticker, yf.ticker.Ticker):
        
            hist = ticker.history(start=start, end=end, interval='1d')
            hist = hist.reindex(columns=['Close'])
            hist['Returns_daily'] = hist['Close'].pct_change().fillna(0)
            hist['Returns'] = (1 + hist['Returns_daily']).cumprod() - 1
            hist = hist.drop(columns=['Returns_daily'])
            
            # print(hist[['Returns_daily','Returns']])    
            
        return hist

 
# d = DataFetcher.get_prices('WTW', 5)
