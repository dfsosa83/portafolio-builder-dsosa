# -*- coding: utf-8 -*-
"""
Created on Tue Mar 18 10:14:31 2025

@author: rblasser
"""

import streamlit as st
from src.components.stock_pool import StockPoolComponent
from src.components.stock_analysis import StockAnalysisComponent
from src.components.macro_analysis import MacroAnalysisComponent
from src.components.settings import SettingsComponent
from src.utils.config_manager import ConfigManager

from utils.logger import AuthSystem
import pandas as pd

class StockAnalyzerApp:
    def __init__(self):
        st.set_page_config(
            page_title="Stock Analyzer",
            page_icon="📈",
            layout="wide"
        )
        self.config_manager = ConfigManager()
        self.auth = AuthSystem()  # Initialize auth system
        self.initialize_session_state()

    def initialize_session_state(self):
        if 'storage_manager' not in st.session_state:
            from src.utils.storage_manager import StorageManager
            st.session_state.storage_manager = StorageManager()
        
        if 'stock_pool' not in st.session_state:
            st.session_state.stock_pool = st.session_state.storage_manager.load_stock_pool()
        
        if 'favorite_stocks' not in st.session_state:
            st.session_state.favorite_stocks = st.session_state.storage_manager.load_favorite_stocks()
        
        if 'config_manager' not in st.session_state:
            st.session_state.config_manager = self.config_manager

    def run(self):
        # Authentication Check
        if not self.auth.is_authenticated():
            self.auth.render_auth_ui()
            return  # Exit early if not authenticated
        
        # Render authenticated UI
        st.title(f"Welcome {st.session_state.username} ({st.session_state.role})")
        
        # Admin-specific features
        if st.session_state.role == 'admin':
            with st.expander("Role Management"):
                new_role = st.text_input("New role name")
                if st.button("Create Role"):
                    self.auth.create_role(new_role, "New system role")
                    
            with st.expander("User Management"):
                users = self.auth.get_all_users()
                df = pd.DataFrame(users)
                st.dataframe(df[['username', 'role', 'created_at']], 
                            use_container_width=True)
                
                # Delete user interface
                del_user = st.selectbox("Select user to delete", 
                                      [u['username'] for u in users])
                if st.button("Delete User"):
                    success, message = self.auth.delete_user(del_user)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

        # Main application UI
        st.sidebar.title("Navigation")
        
        # Check if API keys are configured
        fred_key = self.config_manager.get_api_key('fred_api_key')
        alpha_key = self.config_manager.get_api_key('alpha_vantage_key')
        
        if not (fred_key and alpha_key):
            st.warning("Please configure your API keys in the Settings page")
        
        page = st.sidebar.radio(
            "Select a page",
            ["Stock Pool", "Stock Analysis", "Macro Analysis", "Settings"]
        )

        try:
            if page == "Stock Pool":
                StockPoolComponent().render()
            elif page == "Stock Analysis":
                StockAnalysisComponent().render()
            elif page == "Macro Analysis":
                if self.config_manager.get_feature_flag('enable_macro_analysis'):
                    MacroAnalysisComponent().render()
                else:
                    st.info("Macro Analysis is currently disabled. Enable it in Settings.")
            else:
                SettingsComponent().render()
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

        # Logout button
        st.button("Logout", on_click=self.auth.logout)


if __name__ == "__main__":
    app = StockAnalyzerApp()
    app.run() 