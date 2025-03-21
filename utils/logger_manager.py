# -*- coding: utf-8 -*-
"""
Created on Tue Mar 18 11:33:30 2025

@author: rblasser
"""

import streamlit as st
from sqlalchemy import create_engine, Column, String, DateTime, Boolean, select
from sqlalchemy.orm import sessionmaker, declarative_base
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pandas as pd


DB_PATH = 'sqlite:///auth.db'



class AuthSystem:
    def connection():
        engine = create_engine(DB_PATH)
        return engine