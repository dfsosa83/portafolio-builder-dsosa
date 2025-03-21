# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 10:00:42 2024

@author: rblasser
"""

import streamlit as st
import os
from PIL import Image
import base64
import matplotlib.pyplot as plt
import plotly.express as px


#ASSETS
ICON = os.path.join(os.getcwd(),"assets","360.ico")
ico = Image.open(ICON)

HEADER = os.path.join(os.getcwd(),"assets","prival_360.png")
header = Image.open(HEADER)

LINER = os.path.join(os.getcwd(),"assets","header_line.png")
liner = Image.open(LINER)

contents = open(HEADER, "rb").read()
data_url = base64.b64encode(contents).decode("utf-8")
open(HEADER, "rb").close()

class Utility:
    
    def add_custom_css() -> None:
        st.markdown(
            """
            <style>
            div.st-emotion-cache-6qob1r.eczjsme3 {
                color: white;
                background-color: white;
                
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        
    
    def add_header()-> None:
        
        custom_html = f"""
            <div class="banner">
                <img src="data:image/png;base64,{data_url}">
            </div>
            
            """    
        st.components.v1.html(custom_html)
    

    def add_side_logo() -> None:
        

        # Utility.add_custom_css()       

        st.set_page_config(
            layout="wide",
            page_title="Prival 360 | Portfolio Builder",
            page_icon=ico #"👋",
        )
        
        st.sidebar.image(HEADER, use_container_width =True)


    def liner_path() -> str:
        
        return LINER
       
        
        
    def format_color(s):
        return ['background-color: orange']*len(s) if s.Index else ['background-color: white']*len(s)



    
    def popup_graph(stock, years, data):
        
        data = data.reset_index()
        
        fig, ax = plt.subplots()
        ax.plot(data["Date"], data["Returns"], label="Returns", color="blue")
        ax.set_title(f"{stock}: Daily Returns (last {years} years).")
        ax.set_xlabel("Periods")
        ax.set_ylabel("Returns")
        ax.legend()
        
        return fig
    
    def popup_graphly(stock, years, data, serie):
        
        data = data.reset_index().fillna(0)
        
        if serie == 'Close':
            data = data.rename(columns={'Close':'Daily Closing Prices'})
            y_label = data[data.columns[1]].name
            color = "#FF5733"
        
        if serie == 'Returns':
            data = data.rename(columns={'Returns':'Cumulative Returns'})
            y_label = data[data.columns[2]].name
            color = "#49cb8e"
        
        fig = px.line(
                data,
                x="Date",
                y=f"{y_label}",
                title=f"{stock}: {y_label} (last {years} years).",
                labels={"date": "Date", "value": f"{y_label}"},
                color_discrete_sequence=[color]
            )
        
        fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Value",
                xaxis=dict(showgrid=True),
                yaxis=dict(showgrid=True),
            )

        return fig






