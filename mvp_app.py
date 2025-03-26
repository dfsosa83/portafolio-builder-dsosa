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
import streamlit.components.v1 as components
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
                # Display user management UI
        
        st.button("Logout", on_click=auth.logout, type="primary")
        
        
        asset_class =  st.selectbox(
            "Choose an Asset Class",
            ('ETFs',
            'Fixed Income',
            'Money Market',
            'Stocks'),
            index=None,
            placeholder="Select an asset class...",
        )
        
        
        # ASSET_CLASS IS NOT IN Stocks or ETFs
        if asset_class not in ['Stocks', 'ETFs']:   
        
            query = st.text_input("Search an Asset." )
            
            if len(query) >1:

                res1 = db.read_assets_file()
                res1 = res1[res1['Nombre'].str.upper().str.contains(query.upper())]
                
                if len (res1) == 0:
                    st.warning(f"{query} did not return any results.")
                
                else:
                    securities = res1['Nombre'].drop_duplicates()
                    securities.loc[-1] = 'None'
                    securities.index = securities.index + 1 
                    securities = securities.sort_index()  
                    
                    selected_company = st.selectbox("Select an Asset.", securities)
                    
                    # selected_company = 'LETRAS REP PANAMA 0 08/14/2020'
                    
                    if selected_company != 'None':
                        res2 = res1[res1['Nombre']==selected_company].iloc[0]
                        
                        res2b = res2.T
                        res2b.columns=["Asset Information."]
                        
                        st.dataframe(res2b)
                        
                        if st.button("Add to Portfolio.", icon="✅"):
                            
                            res3 = pd.DataFrame(columns=["Symbol", "Name",
                                                        "Last Price",
                                                            "Score",
                                                            # "P/E Ratio",
                                                            "Asset Class",
                                                            "Allocation (%)"],index=range(1))
                            
                            isin = res2['ISIN']
                            nombre = res2['Nombre']
                            last_price = 0
                            Score = 0
                            pe_ration = 0
                            asset_class = asset_class
                            alloc = 0
                            
                            res3['Symbol'] = isin
                            res3['Name'] = nombre
                            res3['Last Price'] = 0
                            res3['Score'] = 0
                            # res3['P/E Ratio'] = 0
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
                        
                        # print(dfm.T)
                        
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
                                    
                            
                            
                            
    st.header("Portfolio Table.")
    
    # st.text("From the sidebar, add the security of your preference and be aware of the risk profile constraints (review the Risk Matrix).")
    
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
                
                
                                
                st.dataframe(db.read_risk_matrix_file('max_allocation').iloc[:-2,:],
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
                                 
                             st.data_editor(db.read_risk_matrix_file('max_allocation').iloc[:-2,:],
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
        
        agg_classes = db.read_risk_matrix_file('risk_matrix')
        agg_classes = agg_classes[['asset_class', profile_option]]
        
        definicion = agg_classes.iloc[-1]
        
        agg_classes = agg_classes.iloc[:-2,:]
        
        # dfr.columns = profile_optiond
        
        # st.text(definicion)
        
        with st.expander(f'Allocation Limits for {profile_option} Profile.'):
            agg_classes['Allocated'] = 0
            agg_classes['Status'] = 0
            st.dataframe(agg_classes, hide_index=True)
        
    
    st.divider()
    # st.dataframe(manager.df)
    

    edited_df = st.data_editor(
        manager.df,
        column_config={
            # "Risk Profile": st.column_config.NumberColumn("Risk Profile"),
            "Allocation (%)": st.column_config.NumberColumn("Allocation (%)", min_value=0),
        },
        
        disabled=manager.df.columns[:-1],  # Disable editing on other columns if needed
        hide_index=True,
        num_rows = 'dynamic'
    )
    
    # NEW SESSION DATAFRAME
    manager.df = edited_df
    
    # AGGREGATE BY ASSET CLASS
    
    agg_df = manager.df.groupby('Asset Class')['Allocation (%)'].sum()
    print(agg_df)
    
    
    total_w = manager.df['Allocation (%)'].sum()
    
    st.text(f"Total Asset Allocation: {total_w}%")
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    