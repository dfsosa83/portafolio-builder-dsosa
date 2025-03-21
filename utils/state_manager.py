# -*- coding: utf-8 -*-
"""
Created on Wed Mar 19 11:44:05 2025

@author: rblasser
"""

import streamlit as st
import pandas as pd


class DataManager:
    
    
    def __init__(self, key='session_frame'):
        
        self.key = key
        
        if key not in st.session_state:
            st.session_state[key] = pd.DataFrame(columns=["Symbol", "Name",
                                                        "Last Price",
                                                            "Score",
                                                            # "ROE (%)",
                                                            # "Operating Margin (%)",
                                                            # "EPS/Price (%)",
                                                            # "Quick Ratio",
                                                            # "Free Cash Flow ($M)",
                                                            "P/E Ratio",
                                                            # "Recommendation",
                                                            "Asset Class",
                                                            # "Profile Match",
                                                            "Allocation (%)"])
    @property
    def df(self):
        return st.session_state[self.key]
    
    
    def process_data(data):
        
        symbol = data.columns[-1]
        data = pd.pivot_table(data, columns='Symbol', values=symbol, aggfunc='sum').reset_index()
        
        data = data.rename(columns={'index':'Symbol'})
        
        
        data = data.reindex(columns=["Symbol", "Name",
                                    "Last Price",
                                        "Score",
                                        # "ROE (%)",
                                        # "Operating Margin (%)",
                                        # "EPS/Price (%)",
                                        # "Quick Ratio",
                                        # "Free Cash Flow ($M)",
                                        "P/E Ratio",
                                        # "Recommendation",
                                        "Asset Class",
                                        # "Profile Match",
                                        "Allocation (%)"
                                        ]).fillna(0)
        
    
        return data
        
    
    def add_row(self, data):
       new_row = data
       st.session_state[self.key] = pd.concat([self.df, new_row], ignore_index=True)
    
    
    
    
    
    """
    
    # st.dataframe(st.session_state.session_frame, hide_index=True)
    
    
    
    
    cols= init_session_df.columns
    
    
    edited_df = st.data_editor(
        st.session_state.session_frame,
        column_config={
            # "Risk Profile": st.column_config.NumberColumn("Risk Profile"),
            "Weight (%)": st.column_config.NumberColumn("Weight (%)", min_value=0),
        },
        
        disabled=cols[:-1],  # Disable editing on other columns if needed
        hide_index=True,
        num_rows = 'dynamic'
    )
    
    total_w = edited_df['Weight (%)'].sum()
    
    
    
    st.text(f"Total Asset Allocation: {total_w}%")
    
    """