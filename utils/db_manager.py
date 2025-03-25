# -*- coding: utf-8 -*-
"""
Created on Mon Mar 24 10:22:33 2025

@author: rblasser
"""

import sqlite3
from sqlite3 import Error

import pandas as pd
import os


DB_PATH = r'C:\Users\rblasser\OneDrive\Desktop\PORTFOLIO_PRIVAL\mvp\mvp_app\databases'


class DataBases:
    
    def read_risk_matrix():
        
        db_path = os.path.join(DB_PATH, 'risk_table.db')
        con = sqlite3.connect(db_path)

        df = pd.read_sql('select * from allocation_limits', con)
        
        con.close()

        return df
    
    
    def read_risk_matrix_file(sheet_name):
        
        db_path = os.path.join(DB_PATH, 'catalog_db.xlsx')
        
        df = pd.read_excel(db_path, sheet_name=sheet_name)
        
       

        return df
    
    
    
    def read_assets_file():
        
        db_path = os.path.join(DB_PATH, 'filtered_assets.xlsx')
        
        df = pd.read_excel(db_path, sheet_name='assets')

        return df
    
    
    
    
    
    
    
    
    
    
    # def __init__(self, db_path='portfolio.db'):
    #     self.db_path = db_path
    #     self._create_tables()
        
    # def _create_connection(self):
    #     """Create a database connection"""
    #     conn = None
    #     try:
    #         conn = sqlite3.connect(self.db_path)
    #         return conn
    #     except Error as e:
    #         print(e)
    #     return conn

    # def _create_tables(self):
    #     """Initialize database tables"""
    #     sql_asset_class = """
    #     CREATE TABLE IF NOT EXISTS asset_class (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         name TEXT NOT NULL UNIQUE,
    #         description TEXT
    #     );"""
        
    #     sql_risk_matrix = """
    #     CREATE TABLE IF NOT EXISTS risk_matrix (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         asset_class_id INTEGER NOT NULL,
    #         risk_level INTEGER CHECK(risk_level BETWEEN 1 AND 5),
    #         criteria TEXT,
    #         FOREIGN KEY (asset_class_id) REFERENCES asset_class (id)
    #     );"""
        
    #     sql_portfolio_viewer = """
    #     CREATE TABLE IF NOT EXISTS portfolio_viewer (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         name TEXT NOT NULL,
    #         configuration TEXT
    #     );"""
        
    #     try:
    #         conn = self._create_connection()
    #         cursor = conn.cursor()
    #         cursor.execute(sql_asset_class)
    #         cursor.execute(sql_risk_matrix)
    #         cursor.execute(sql_portfolio_viewer)
    #         conn.commit()
    #     except Error as e:
    #         print(e)
    #     finally:
    #         if conn:
    #             conn.close()

    # # Asset Class CRUD
    # def create_asset_class(self, name, description):
    #     conn = self._create_connection()
    #     try:
    #         sql = '''INSERT INTO asset_class(name, description) VALUES(?,?)'''
    #         cursor = conn.cursor()
    #         cursor.execute(sql, (name, description))
    #         conn.commit()
    #         return cursor.lastrowid
    #     except Error as e:
    #         print(e)
    #     finally:
    #         if conn:
    #             conn.close()

    # def read_asset_classes(self):
    #     conn = self._create_connection()
    #     try:
    #         cursor = conn.cursor()
    #         cursor.execute("SELECT * FROM asset_class")
    #         return cursor.fetchall()
    #     except Error as e:
    #         print(e)
    #     finally:
    #         if conn:
    #             conn.close()

    # # Risk Matrix CRUD with role control
    # def create_risk_matrix(self, asset_class_id, risk_level, criteria, role):
    #     if role != 'admin':
    #         raise PermissionError("Admin rights required for this operation")
            
    #     conn = self._create_connection()
    #     try:
    #         sql = '''INSERT INTO risk_matrix(asset_class_id, risk_level, criteria)
    #                  VALUES(?,?,?)'''
    #         cursor = conn.cursor()
    #         cursor.execute(sql, (asset_class_id, risk_level, criteria))
    #         conn.commit()
    #         return cursor.lastrowid
    #     except Error as e:
    #         print(e)
    #     finally:
    #         if conn:
    #             conn.close()

    # # def read_risk_matrix(self, role):
    # #     conn = self._create_connection()
    # #     try:
    # #         cursor = conn.cursor()
    # #         cursor.execute("SELECT * FROM risk_matrix")
    # #         return cursor.fetchall()
    # #     except Error as e:
    # #         print(e)
    # #     finally:
    # #         if conn:
    # #             conn.close()

    # def update_risk_matrix(self, matrix_id, asset_class_id, risk_level, criteria, role):
    #     if role != 'admin':
    #         raise PermissionError("Admin rights required for this operation")
            
    #     conn = self._create_connection()
    #     try:
    #         sql = '''UPDATE risk_matrix
    #                  SET asset_class_id = ?, risk_level = ?, criteria = ?
    #                  WHERE id = ?'''
    #         cursor = conn.cursor()
    #         cursor.execute(sql, (asset_class_id, risk_level, criteria, matrix_id))
    #         conn.commit()
    #         return cursor.rowcount
    #     except Error as e:
    #         print(e)
    #     finally:
    #         if conn:
    #             conn.close()

    # def delete_risk_matrix(self, matrix_id, role):
    #     if role != 'admin':
    #         raise PermissionError("Admin rights required for this operation")
            
    #     conn = self._create_connection()
    #     try:
    #         sql = 'DELETE FROM risk_matrix WHERE id=?'
    #         cursor = conn.cursor()
    #         cursor.execute(sql, (matrix_id,))
    #         conn.commit()
    #         return cursor.rowcount
    #     except Error as e:
    #         print(e)
    #     finally:
    #         if conn:
    #             conn.close()

    # # Portfolio Viewer CRUD
    # def create_portfolio_viewer(self, name, configuration):
    #     conn = self._create_connection()
    #     try:
    #         sql = '''INSERT INTO portfolio_viewer(name, configuration) VALUES(?,?)'''
    #         cursor = conn.cursor()
    #         cursor.execute(sql, (name, configuration))
    #         conn.commit()
    #         return cursor.lastrowid
    #     except Error as e:
    #         print(e)
    #     finally:
    #         if conn:
    #             conn.close()

    # def read_portfolio_viewers(self):
    #     conn = self._create_connection()
    #     try:
    #         cursor = conn.cursor()
    #         cursor.execute("SELECT * FROM portfolio_viewer")
    #         return cursor.fetchall()
    #     except Error as e:
    #         print(e)
    #     finally:
    #         if conn:
    #             conn.close()
