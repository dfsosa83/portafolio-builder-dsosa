# -*- coding: utf-8 -*-
"""
Created on Mon Mar 24 10:22:33 2025

@author: rblasser
"""

import os
import pandas as pd
import streamlit as st

from sqlalchemy import create_engine



DB_PATH = os.path.join(os.getcwd(),'databases')

class DataBases:
    
    def db_path():
        
        DB_PATH = os.path.join(os.getcwd(),'databases')

        return os.path.exists(DB_PATH)
    
    
    
    def db_connect(database):
        
        db_path = os.path.join(DB_PATH, database)
        engine = create_engine("sqlite:///"+db_path, echo=True)
        con = engine.connect()

        
        return con
        
    
    
    @st.cache_data
    def read_risk_matrix(table_name): # max_allocation | risk_matrix
        
        database = 'risk_db.db'
        con = DataBases.db_connect(database)
        df = pd.read_sql(f'select * from {table_name}', con)
        
        con.close()

        return df
    
    
    # FONDOS PRIVAL (tabla prival_funds) Y TERCEROS (tabla assets)
    @st.cache_data
    def read_assets_funds(table_name): # assets | prival_funds
        
        database = 'funds_db.db'
        con = DataBases.db_connect(database)
        df = pd.read_sql(f'select * from {table_name}', con)
        
        con.close()

        return df
    
    