import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import requests
from src.models.moo_optimizer import portfolio_optimizer
from src.models.stock_metrics import StockMetrics
from src.utils.data_fetcher import DataFetcher
from src.templates.factsheet import generate_pdf_report
from pypfopt import EfficientFrontier, risk_models, expected_returns
import plotly.express as px
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta
import io


class StockPoolComponent:
    def __init__(self):
        self.stock_metrics = StockMetrics()
        self.data_fetcher = DataFetcher()
        if 'stock_pool' not in st.session_state:
            st.session_state.stock_pool = {}
        if 'clear_search' not in st.session_state:
            st.session_state.clear_search = False

    def search_stocks(self, query):
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

    def handle_search_change(self):
        if 'stock_search_input' in st.session_state:
            st.session_state.search_query = st.session_state.stock_search_input
            st.session_state.selected_stock = None

    def add_stock(self, symbol, name):
        if symbol in st.session_state.stock_pool:
            st.warning(f"{symbol} is already in your stock pool")
            return False
        
        st.session_state.stock_pool[symbol] = name
        if hasattr(st.session_state, 'storage_manager'):
            st.session_state.storage_manager.save_stock_pool(st.session_state.stock_pool)
        return True

    def remove_stocks(self, symbols_to_remove):
        for symbol in symbols_to_remove:
            if symbol in st.session_state.stock_pool:
                del st.session_state.stock_pool[symbol]
        
        if hasattr(st.session_state, 'storage_manager'):
            st.session_state.storage_manager.save_stock_pool(st.session_state.stock_pool)
        
        st.session_state.show_remove_message = f"Removed {len(symbols_to_remove)} stock(s) from your stock pool"
        if 'stock_metrics_results' in st.session_state:
            del st.session_state.stock_metrics_results
        st.rerun()


    def render(self):
        st.title("Portfolio Builder")
        
        if 'show_remove_message' in st.session_state:
            st.success(st.session_state.show_remove_message)
            del st.session_state.show_remove_message

        search_container = st.container()
        with search_container:
            if 'search_query' not in st.session_state:
                st.session_state.search_query = ''
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                default_value = "" if st.session_state.clear_search else st.session_state.get('stock_search_input', '')
                
                search_query = st.text_input(
                    "Search by Symbol or Company Name",
                    value=default_value,
                    key="stock_search_input",
                    on_change=self.handle_search_change,
                    help="Type to search stocks",
                    label_visibility="visible"
                )
                
                if st.session_state.clear_search:
                    st.session_state.clear_search = False
                
                if 'selected_stock' not in st.session_state:
                    st.session_state.selected_stock = None
                
                if search_query and len(search_query) >= 2:
                    suggestions = self.search_stocks(search_query)
                    if suggestions:
                        selected = st.selectbox(
                            "Select a stock",
                            options=[{"label": "Select a stock...", "value": None}] + suggestions,
                            format_func=lambda x: x["label"] if x and isinstance(x, dict) and "label" in x else "Select a stock...",
                            key="stock_selector",
                            label_visibility="collapsed"
                        )
                        
                        if selected and isinstance(selected, dict) and selected.get("value"):
                            st.session_state.selected_stock = selected
            
            with col2:
                if st.button("Add Stock", key="add_stock_button"):
                    if (st.session_state.selected_stock and 
                        isinstance(st.session_state.selected_stock, dict) and 
                        st.session_state.selected_stock.get("value")):
                        
                        selected_value = st.session_state.selected_stock["value"]
                        if isinstance(selected_value, dict) and "symbol" in selected_value and "name" in selected_value:
                            symbol = selected_value["symbol"]
                            name = selected_value["name"]
                            
                            if self.add_stock(symbol, name):
                                st.success(f"Added {symbol} to your stock pool")
                                st.session_state.clear_search = True
                                st.session_state.selected_stock = None
                                st.session_state.search_query = ''
                                if 'stock_metrics_results' in st.session_state:
                                    del st.session_state.stock_metrics_results
                                st.rerun()
                    else:
                        st.warning("Please select a stock first")

        if st.session_state.stock_pool:
            st.subheader("Current Portfolio")
            stock_list = list(st.session_state.stock_pool.items())
            
            pool_container = st.container()
            
            with pool_container:
                if 'stock_metrics_results' not in st.session_state:
                    results = []
                    for symbol, name in stock_list:
                        with st.spinner(f"Analyzing {symbol}..."):
                            metrics = self.stock_metrics.get_stock_metrics(symbol)
                            if metrics:
                                metrics['Symbol'] = symbol
                                metrics['Company'] = name
                                results.append(metrics)
                    st.session_state.stock_metrics_results = results
                
                results = st.session_state.stock_metrics_results
                
                if results:
                    try:
                        df = pd.DataFrame(results).copy()
                        df = df[df['Symbol'].isin(st.session_state.stock_pool.keys())]
                        
                        if not df.empty:
                            df = df.reset_index(drop=True)
                            df.index = range(1, len(df) + 1)
                            df.index.name = 'Number'
                            
                            cols = ['Symbol', 'Company'] + [col for col in df.columns if col not in ['Symbol', 'Company']]
                            df = df[cols]
                            
                            # Add a checkbox column for selection
                            df['Select'] = False
                            
                            # Use st.data_editor instead of st.dataframe
                            edited_df = st.data_editor(
                                df,
                                hide_index=False,
                                column_config={
                                    "Select": st.column_config.CheckboxColumn(
                                        "Select",
                                        help="Select stocks to delete",
                                        default=False
                                    )
                                },
                                disabled=df.columns.drop('Select'),
                                key="stock_pool_editor"
                            )
                            
                            # Add a delete button

                        if st.button("Delete Selected Stocks"):
                            stocks_to_delete = edited_df[edited_df['Select']]['Symbol'].tolist()
                            if stocks_to_delete:
                                self.remove_stocks(stocks_to_delete)
                            else:
                                st.warning("No stocks selected for deletion")

                        # New Portfolio Optimization section
                        st.header("Portfolio Optimization")
                        
                        with st.expander("Optimization Parameters", expanded=False):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                utility_type = st.selectbox(
                                    "Utility Function Type",
                                    options=['quadratic', 'power'],
                                    index=1,
                                    help="Select between quadratic (mean-variance) or power utility function"
                                )
                                gamma = st.number_input(
                                    "Risk Aversion (γ)",
                                    min_value=1.0,
                                    max_value=10.0,
                                    value=3.0,
                                    step=0.5,
                                    help="Risk aversion parameter for power utility"
                                )
                                max_turnover = st.slider(
                                    "Maximum Turnover",
                                    min_value=0.0,
                                    max_value=1.0,
                                    value=0.5,
                                    help="Maximum allowed portfolio turnover (0-1)"
                                )

                            with col2:
                                risk_free_rate = st.number_input(
                                    "Risk-Free Rate (%)",
                                    min_value=0.0,
                                    max_value=10.0,
                                    value=4.5,
                                    step=0.1
                                ) / 100
                                mar = st.number_input(
                                    "Minimum Acceptable Return (%)",
                                    min_value=-5.0,
                                    max_value=5.0,
                                    value=1.0,
                                    step=0.5
                                ) / 100
                                max_drawdown = st.slider(
                                    "Max Drawdown",
                                    min_value=0.0,
                                    max_value=1.0,
                                    value=0.5,
                                    help="Maximum allowed drawdown (0-1)"
                                )

                            with col3:
                                alpha_l1 = st.number_input(
                                    "L1 Regularization",
                                    min_value=0.0,
                                    max_value=1.0,
                                    value=0.0,
                                    step=0.01
                                )
                                alpha_l2 = st.number_input(
                                    "L2 Regularization",
                                    min_value=0.0,
                                    max_value=1.0,
                                    value=0.0,
                                    step=0.01
                                )
                                cost_factor = st.number_input(
                                    "Transaction Cost (%)",
                                    min_value=0.0,
                                    max_value=5.0,
                                    value=0.5,
                                    step=0.1
                                ) / 100

                        # Move the "Allocate Optimal Portfolio" button here
                        if st.button("📊 Allocate Optimal Portfolio"):
                            with st.spinner("Allocating portfolio..."):
                                
                                symbols = list(st.session_state.stock_pool.keys())

                                try:
                                    # Call the optimizer with parameters
                                    results = portfolio_optimizer(
                                        symbols,
                                        utility_type=utility_type,
                                        gamma=gamma,
                                        risk_free_rate=risk_free_rate,
                                        mar=mar,
                                        max_turnover=max_turnover,
                                        max_drawdown=max_drawdown,
                                        alpha_l1=alpha_l1,
                                        alpha_l2=alpha_l2,
                                        cost_factor=cost_factor
                                    )
                                    
                                    # Wrap the results in a "Results" section
                                    st.header("Results")

                                    # Display metrics
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.metric("Sharpe Ratio", f"{results['sharpe']:.2f}")
                                        st.metric("Annual Return", f"{results['annual_return']:.1%}")
                                        
                                    with col2:
                                        st.metric("Max Drawdown", f"{results['max_drawdown']:.1%}")
                                        st.metric("Annual Volatility", f"{results['annual_volatility']:.1%}")
                                        
                                    with col3:
                                        portfolio_value = st.number_input("Portfolio Value ($)", 
                                                                        min_value=1000, 
                                                                        value=10000,
                                                                        step=1000)

                                    # Plot cumulative returns
                                    fig = px.line(
                                        title="Portfolio Performance vs Equal Weight",
                                        labels={'value': 'Return', 'variable': 'Strategy'}
                                    )
                                    fig.add_scatter(x=results['cumulative_returns'].index, 
                                                y=results['cumulative_returns'], 
                                                name="Optimal Portfolio")
                                    fig.add_scatter(x=results['equal_cumulative'].index, 
                                                y=results['equal_cumulative'], 
                                                name="Equal Weight")
                                    st.plotly_chart(fig, use_container_width=True)

                                    # Plot pie chart
                                    fig_pie = px.pie(results['weights_df'], 
                                                values='Weight', 
                                                names=results['weights_df'].index,
                                                title="Portfolio Allocation")
                                    st.plotly_chart(fig_pie, use_container_width=True)

                                    # Display allocation table
                                    st.subheader("Optimal Allocation")
                                    st.dataframe(
                                        results['allocation_df'].style.format({
                                            'Weight': '{:.1%}',
                                            'Amount ($)': '${:,.2f}'
                                        }),
                                        use_container_width=True
                                    )

                                    # Generate PDF report
                                    pdf_buffer = generate_pdf_report(
                                        portfolio_value,
                                        results['sharpe'],
                                        results['annual_return'],
                                        results['annual_volatility'],
                                        results['max_drawdown'],
                                        results['weights_df'].to_dict()['Weight'],
                                        results['img_buffer']
                                    )

                                    st.download_button(
                                        label="📥 Download PDF Report",
                                        data=pdf_buffer,
                                        file_name="portfolio_report.pdf",
                                        mime="application/pdf"
                                    )
                                    
                                except Exception as e:
                                    st.error(f"Portfolio allocation failed: {str(e)}")
                    except:
                        pass