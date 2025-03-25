# -*- coding: utf-8 -*-
"""
Created on Mon Mar 24 16:59:35 2025

@author: rblasser
"""

import pandas as pd
import sqlite3
import os

path = r'C:\Users\rblasser\OneDrive\Desktop\PORTFOLIO_PRIVAL\mvp\mvp_app\catalog\catalog_db.xlsx'

df = pd.read_excel(path, sheet_name='risk_matrix')


df1 = pd.melt(df, id_vars=['asset_class'],
        value_vars=['Conservative', 'Moderate', 'Balanced', 'Growth',
       'Aggressive'])






db_path = r'C:\Users\rblasser\OneDrive\Desktop\PORTFOLIO_PRIVAL\mvp\mvp_app\catalog\catalog_db.xlsx'

db_path='risk_table.db'

conn = sqlite3.connect(db_path)


df1.to_sql(name='allocation_limits', con=conn)

conn.close()


# READ ASSETS


p = r'C:\Users\rblasser\OneDrive\Desktop\PORTFOLIO_PRIVAL\mvp\mvp_app\databases'

f = 'filtered_assets.csv'


dfx = pd.read_csv(os.path.join(p,f))


dfx.to_excel(os.path.join(p,'filtered_assets.xlsx'))
