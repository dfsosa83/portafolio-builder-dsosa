# -*- coding: utf-8 -*-
"""
Created on Tue Mar 18 08:39:16 2025

@author: rblasser
"""

import pandas as pd
import yfinance as yf
import streamlit as st

from utils.logger import AuthSystem
from utils.utility import Utility as util
from utils.state_manager import DataManager

from utils.metrics import StockMetrics as metrics
from utils.data_fetcher import DataFetcher as fetch
from utils.db_manager import DataBases as db


auth = AuthSystem()
metric = metrics()
manager = DataManager()

if not auth.is_authenticated():
    
    col_1, col_2, col_3 = st.columns(3)
    with col_2:
        container = st.container()
        container.title("Portfolio Builder.")
        auth.render_auth_ui()
        st.image(util.liner_path())
        
else:
    
    with st.sidebar:
        
        util.add_side_logo()
        util.add_custom_css()
        
        st.title("Welcome to the Portfolio Builder.")
        st.write(f"**Active Session: {st.session_state.username} [{st.session_state.role}]**")
        
        # Admin-specific features
        if st.session_state.role == 'admin':
            with st.expander("Role Management"):
                new_role = st.text_input("New role name")
                if st.button("Create Role"):
                    auth.create_role(new_role, "New system role")
                    
            with st.expander("User Management"):
                users = auth.get_all_users()
        
        
        asset_class =  st.selectbox(
            "Choose an Asset Class",
            ('ETFs',
            'Fixed Income',
            'Money Market',
            'Private Funds',
            'Stocks'),
            index=None,
            placeholder="Select an asset class...",
        )
        
        # ASSET_CLASS IS FONDOS PRIVAL
        if asset_class in ['Private Funds']:
            
            query = st.text_input("Search a Private Fund.")
            
            if len(query) >1:
                
                res1 = db.read_assets_funds('prival_funds').fillna(0)
                res1 = res1[res1['Fondo'].str.upper().str.contains(query.upper())]
                
                if len (res1) == 0:
                    st.warning(f"{query} did not return any results.")
                
                else:
                    fondos = res1['Fondo'].drop_duplicates()
                    fondos.loc[-1] = 'None'
                    fondos.index = fondos.index + 1 
                    fondos = fondos.sort_index()  
                    
                    selected_fund = st.selectbox("Select a Fund.", fondos)
                    
                    if selected_fund != 'None':
                        res2 = res1[res1['Fondo']==selected_fund].iloc[0]
                        
                        st.dataframe(res2)
                        
                        if st.button("Add to Portfolio.", icon="✅"):
                            
                            res3 = pd.DataFrame(columns=["Symbol", "Name",
                                                        "Last Price",
                                                            "Sector",
                                                            # "P/E Ratio",
                                                            "Asset Class",
                                                            "Allocation (%)"],index=range(1))
                            
                            
                            res2 = pd.DataFrame(res2).T
                            
                            isin = res2['Fondo']
                            nombre = res2['Fondo']
                            last_price = res2['Inversión Mínima']
                            sector = 'Fund'
                            pe_ration = 0
                            asset_class = asset_class
                            alloc = 0
                            
                            res3['Symbol'] = isin
                            res3['Name'] = nombre
                            res3['Last Price'] = last_price
                            res3['Sector'] = sector
                            res3['Asset Class'] =  asset_class
                            res3['Allocation (%)'] = 0
                            
                            print("ISIN",isin)
                            
                            manager.add_row(res3)
                        
        
        # ASSET_CLASS IS FIXED INCOME
        elif asset_class in ['Fixed Income']:   
        
            query = st.text_input("Search an Asset." )
            
            if len(query) >1:

                res1 = db.read_assets_funds('assets')
                res1 = res1[res1['Nombre'].str.upper().str.contains(query.upper())]
                
                if len (res1) == 0:
                    st.warning(f"{query} did not return any results.")
                
                else:
                    securities = res1['Nombre'].drop_duplicates()
                    securities.loc[-1] = 'None'
                    securities.index = securities.index + 1 
                    securities = securities.sort_index()  
                    
                    selected_company = st.selectbox("Select an Asset.", securities)
                    
                    
                    if selected_company != 'None':
                        res2 = res1[res1['Nombre']==selected_company].iloc[0]
                        
                        res2b = res2.T
                        res2b.columns=["Asset Information."]
                        
                        st.dataframe(res2b)
                        
                        if st.button("Add to Portfolio.", icon="✅"):
                            
                            res3 = pd.DataFrame(columns=["Symbol", "Name",
                                                        "Last Price",
                                                            "Sector",
                                                            "Asset Class",
                                                            "Allocation (%)"],index=range(1))
                            
                            isin = res2['ISIN']
                            nombre = res2['Nombre']
                            last_price = 0
                            sector = res2['DESC.INDUSTRY']
                            pe_ration = 0
                            asset_class = asset_class
                            alloc = 0
                            
                            res3['Symbol'] = isin
                            res3['Name'] = nombre
                            res3['Last Price'] = 0
                            res3['Sector'] = sector
                            res3['Asset Class'] =  asset_class
                            res3['Allocation (%)'] = 0
                            
                            print("ISIN",isin)
                            
                            manager.add_row(res3)
        
        # ASSET_CLASS IS IN Stocks or ETFs
        elif asset_class in ['Stocks', 'ETFs']: 
        
            query = st.text_input("Search a Company." )
            
            if len(query) >1:
                
                res1 = fetch.search_stocks(query)
                
                if len (res1) == 0:
                    st.warning(f"{query} did not return any results.")
    
                else:
                
                    d1 = []
                    for each_res in res1:
                        d1.append(each_res['value'])
                    
                    df1 = pd.DataFrame.from_dict(d1, orient='columns').reset_index()
                    df1['concat'] = df1['symbol'] + " - " + df1['name']
                    
                    securities = df1['concat']
                    
                    securities.loc[-1] = 'None'
                    securities.index = securities.index + 1 
                    securities = securities.sort_index()  
                    
                    
                    selected_company = st.selectbox("Select a Company.", securities)
                    
                    if selected_company != 'None':
                        
                        stock = df1[df1['concat'] == selected_company]['symbol'].values
                        stock = stock[0]
                        
                        company = df1[df1['concat'] == selected_company]['name'].values
                        company = company[0]
                        
                        dfm = pd.DataFrame.from_dict(metric.get_stock_metrics(stock), 
                                                     orient='index').reset_index()
                        
                        dfm.iloc[-1] = ['Name', company]
                        
                        dfm.columns=['Symbol',stock]
                        
                        
                        if st.button("Add to Portfolio.", icon="✅"):
                           # Processed DF
                           dfx = DataManager.process_data(dfm,asset_class)
                           
                           # Add to Session DF
                           manager.add_row(dfx)
                           
                        st.dataframe(dfm, hide_index=True)
                        
                        years = st.slider("Years of History.", 1, 10, 5)
                        if st.button("Show Plot 📈"):
                            with st.expander("View Historical Data."):
                                
                                df2 = fetch.get_prices(stock,years)
                                
                                # print(df2[['Returns_daily','Returns']])
                                
                                # st.pyplot(util.popup_graph(stock,5,df2))
                                st.plotly_chart(util.popup_graphly(stock,years,df2,'Close'), use_container_width=True)
    
                                st.plotly_chart(util.popup_graphly(stock,years,df2,'Returns'), use_container_width=True)
                        
                        with st.container(border=True):
                            
                                ticker = yf.Ticker(stock)
                                info = ticker.info
                                
                                
                                # Display company details
                                st.subheader(f"Details for {stock.upper()}")
                                st.write(f"**Company Name:** {info.get('longName', 'N/A')}")
                                st.write(f"**Sector:** {info.get('sector', 'N/A')}")
                                try:
                                    st.write(f"**Market Cap:** {info.get('marketCap', 'N/A')/1000000:,.2f} Millions")
                                except:
                                    st.write(f"**Market Cap:** {info.get('marketCap', 'N/A')}")
                                    
                                try:
                                    st.write(f"**Number of Employees:** {info.get('fullTimeEmployees', 'N/A'):,}")
                                except:
                                    st.write(f"**Number of Employees:** {info.get('fullTimeEmployees', 'N/A')}")   
                                    
                                # Optional: Display additional information
                                with st.expander("More Details"):
                                    st.write(f"**City:** {info.get('city', 'N/A')}, **State:** {info.get('state', 'N/A')}, **Country:** {info.get('country', 'N/A')}")
                                    st.write(f"**Business Summary:** {info.get('longBusinessSummary', 'N/A')}")
                                    
                            
    col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns(10)      
    
    with col10:                  
        st.button("Logout", on_click=auth.logout, type="primary")                        
    
    st.header("Portfolio Table.")
        
    col1, col2 = st.columns([3,1])
    
    with col1:
        with st.expander("**Instructions.**"):
            st.markdown("""
                        
                        - **Access the Sidebar**: Use the search bar to find preferred assets.
                        
                        - **Search & Select**: Navigate to the "Add to Portfolio" section in the app’s sidebar.
        
                        - **Risk Profile Check**: Cross-reference the Risk Matrix to ensure the security aligns with the client’s risk profile .
        
                        - **Allocation Preview**: Review how the addition impacts the portfolio’s risk-return balance in real time.
                        
                        - **Proposal Generation**: Press the PDF Generation button to export the report.
                        
                        """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        
        with st.container(border=True, height=185):
            
            client_name = st.text_input("Introduce your client's full name." )
            client_email = st.text_input("Introduce your client's email address." )
            
        
    
    with col2:
        container = st.container(border=True, height=145)
        col1, col2 = container.columns([3,1])
        with col1:
            
            profile_option = st.selectbox(
                "Choose a Risk Profile Rating",
                ("Conservative",
                    "Moderate",
                    "Balanced",
                    "Growth",
                    "Aggressive"),
                index=None,
                placeholder="Select a risk profile...",
            )
            
            st.write("You selected:", profile_option)
            
         
        with col2:
            st.markdown('')
            st.markdown('')
            # st.button("Risk Matrix", type="primary")
            
            with st.popover("Risk Matrix", use_container_width=False):
                
                st.subheader("Asset Allocation Limits by Risk Profile.")
                
                st.markdown("""
                               <style>
                               .stPopover .stPopoverContent {
                                   max-width: 1200px !important;
                               }
                               </style>
                               """, unsafe_allow_html=True)
                
                
                df_alloc = db.read_risk_matrix('max_allocation').iloc[:-2,:]           
                st.dataframe(df_alloc,
                             hide_index = True,
                             width=1300, height=250)
                
                
                if st.session_state.role == 'admin': 
                    with st.expander("Edit Risk Matrix"):
                             st.markdown("""
                                            <style>
                                            .stPopover .stPopoverContent {
                                                max-width: 1500px !important;
                                            }
                                            </style>
                                            """, unsafe_allow_html=True)
                                 
                             st.data_editor(df_alloc,
                                          hide_index = True,
                                          num_rows = 'dynamic',
                                          width=1500, height=250)
                             
                             st.button("Save Risk Matrix", type="primary")
                                        
                    
                else:
                    st.button("Edit Risk Matrix", disabled=True, type="primary")


    st.divider()
    
    with st.expander('Add Custom Asset.'):
        st.dataframe(pd.DataFrame())

    
    if profile_option is not None:
        
        dfr = pd.DataFrame(columns=['ETFs',
        'Fixed Income',
        'Money Market',
        'Stocks'], index=range(1)).T
        
        
        agg_classes = db.read_risk_matrix('risk_matrix')
        
        agg_classes = agg_classes[['asset_class', profile_option]]
        
        definicion = agg_classes.iloc[-1]
        
        agg_classes = agg_classes.iloc[:-2,:]
        

        with st.expander(f'Allocation Limits for {profile_option} Profile.'):
            
             if st.button("Evaluate", disabled=False, type="secondary"):
                agg_classes[profile_option] = agg_classes[profile_option] * 100
    
                agg_classes = agg_classes.rename(columns={profile_option:f"{profile_option} (%)"})
                
                agg_classes = agg_classes.set_index('asset_class')
                
                
                st.markdown("""
                    <style>
                    .dataframe th, .dataframe td {
                        text-align: center;
                    }
                    </style>
                    """, unsafe_allow_html=True)
                
                # AGG PORTFOLIO BY CLASS
                agg_port = manager.df.groupby('Asset Class')['Allocation (%)'].sum()
                
                agg_classes = agg_classes.merge(agg_port, left_index=True, right_index=True, how='left').fillna(0)
                
                
                # Total
                total_row = agg_classes.sum().to_frame().T
                total_row.index = ['Total']  # Rename index
                agg_classes = pd.concat([agg_classes, total_row], ignore_index=False)
                
                agg_classes = agg_classes.rename(columns={'Allocation (%)':'Allocated (%)'})
                    
                
                # EXTRA COLUMNS
                agg_classes['Status'] = agg_classes.apply(lambda row: "✅" if row['Allocated (%)'] <= row[f"{profile_option} (%)"] else "⛔", axis=1)
                
                st.dataframe(agg_classes, hide_index=False)
        
    
    st.divider()

    # NEW SESSION DATAFRAME
    edited_df = st.data_editor(
        st.session_state.session_frame,
        column_config={
            "Allocation (%)": st.column_config.NumberColumn("Allocation (%)", min_value=0),
        },
        disabled=st.session_state.session_frame.columns[:-1],  # Disable editing on other columns if needed
        hide_index=True,
        num_rows='dynamic'
    )
    
    
    # Update session state with the edited dataframe
    if not edited_df.equals(st.session_state.session_frame):
        st.session_state.session_frame = edited_df.copy()
        

    
    # AGGREGATE BY ASSET CLASS
    agg_df = manager.df.groupby('Asset Class')['Allocation (%)'].sum()
    
    
    total_w = manager.df['Allocation (%)'].sum()
    
    st.text(f"Total Asset Allocation: {total_w}%")
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    