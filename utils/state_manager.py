# -*- coding: utf-8 -*-
"""
Created on Wed Mar 19 11:44:05 2025

@author: rblasser
"""

import streamlit as st
import pandas as pd
import yfinance as yf

class DataManager:
    
    
    def __init__(self, key='session_frame'):
        
        self.key = key
        
        if key not in st.session_state:
            st.session_state[key] = pd.DataFrame(columns=["Symbol", "Name",
                                                        "Last Price",
                                                            "Sector",
                                                            # "ROE (%)",
                                                            # "Operating Margin (%)",
                                                            # "EPS/Price (%)",
                                                            # "Quick Ratio",
                                                            # "Free Cash Flow ($M)",
                                                            # "P/E Ratio",
                                                            # "Recommendation",
                                                            "Asset Class",
                                                            # "Profile Match",
                                                            "Allocation (%)"])
    @property
    def df(self):
        return st.session_state[self.key]
    
    
    @df.setter  
    def df(self, value):
        if not isinstance(value, pd.DataFrame):
            raise ValueError("Value must be a pandas DataFrame")
        st.session_state[self.key] = value
       
       
    
    def process_data(data, asset_class):
        
        symbol = data.columns[-1]
        data = pd.pivot_table(data, columns='Symbol', values=symbol, aggfunc='sum').reset_index()
        
        data = data.rename(columns={'index':'Symbol'})
        
        
        data = data.reindex(columns=["Symbol", "Name",
                                    "Last Price",
                                        "Sector",
                                        # "ROE (%)",
                                        # "Operating Margin (%)",
                                        # "EPS/Price (%)",
                                        # "Quick Ratio",
                                        # "Free Cash Flow ($M)",
                                        # "P/E Ratio",
                                        # "Recommendation",
                                        "Asset Class",
                                        # "Profile Match",
                                        "Allocation (%)"
                                        ]).fillna(0)
        
        
        stock = yf.Ticker(symbol)
        info = stock.info
        
        sector = info.get('sector', '')
        
        
        data['Asset Class'] = asset_class
        data['Sector'] = sector
        
        return data
        
    
    def add_row(self, data):
        
       print(data)
       new_row = data
       st.session_state[self.key] = pd.concat([self.df, new_row], ignore_index=True)
    
    
    