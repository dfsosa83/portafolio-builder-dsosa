# -*- coding: utf-8 -*-
"""
Created on Thu Mar 20 12:03:31 2025

@author: rblasser
"""

import pandas as pd
import os
import streamlit as st


# import snowflake.connector
import sqlalchemy
from sqlalchemy import create_engine
from snowflake.sqlalchemy import URL