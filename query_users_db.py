# -*- coding: utf-8 -*-
"""
Created on Tue Mar 18 08:46:40 2025

@author: rblasser
"""

# Run this once to update existing databases
from utils.logger import Base, AuthSystem


auth = AuthSystem()

# DROP TABLE
Base.metadata.drop_all(auth.engine)  # Warning: Deletes existing data!



Base.metadata.create_all(auth.engine)

# QUERY TABLE
import sqlite3

with sqlite3.connect('auth.db') as conn:
           cursor = conn.cursor()
          
cursor.execute("SELECT * FROM users")
cursor.fetchall()
       
# Validate role existence
new_role = ""
cursor.execute("SELECT name FROM roles WHERE name=?", (new_role,))
       

# Update role with validation
success, message = auth.update_user_role("rb1", "admin")
print(f"Success: {success}, Message: {message}")