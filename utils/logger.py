# -*- coding: utf-8 -*-
"""
Created on Mon Mar 17 12:03:59 2025

@author: rblasser
"""

# auth_manager.py (updated)
import streamlit as st
from sqlalchemy import create_engine, Column, String, DateTime, Boolean, select
from sqlalchemy.orm import sessionmaker, declarative_base
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pandas as pd

from utils.utility import Utility as util

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    username = Column(String(50), primary_key=True)
    password_hash = Column(String(128))
    role = Column(String(20), nullable=False, default='user')  # Default role
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)

class Role(Base):
    __tablename__ = 'roles'
    name = Column(String(20), primary_key=True)
    description = Column(String(255))

class AuthSystem:
    def __init__(self, db_url='sqlite:///auth.db'):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
        # Initialize default roles
        with self.Session() as session:
            if not session.get(Role, 'user'):
                session.add(Role(name='user', description='Regular user'))
            if not session.get(Role, 'admin'):
                session.add(Role(name='admin', description='System administrator'))
            session.commit()

        # Initialize session state
        st.session_state.setdefault('authenticated', False)
        st.session_state.setdefault('username', None)
        st.session_state.setdefault('role', None)

    # User Management
    def register_user(self, username, password, role='user'):
        with self.Session() as session:
            if session.get(User, username):
                return False, "Username exists"
            
            if not session.get(Role, role):
                return False, "Invalid role"
            
            hashed_pw = generate_password_hash(password, method='scrypt')
            new_user = User(username=username, 
                          password_hash=hashed_pw,
                          role=role)
            session.add(new_user)
            session.commit()
            return True, "Registration successful"

    def authenticate_user(self, username, password):
        with self.Session() as session:
            user = session.get(User, username)
            if user and check_password_hash(user.password_hash, password):
                user.last_login = datetime.utcnow()
                session.commit()
                st.session_state.update({
                    'authenticated': True,
                    'username': username,
                    'role': user.role
                })
                return True
        return False

    # Role Management
    def create_role(self, name, description):
        with self.Session() as session:
            if session.get(Role, name):
                return False, "Role exists"
            session.add(Role(name=name, description=description))
            session.commit()
            return True, "Role created"

    def get_all_roles(self):
        with self.Session() as session:
            return session.scalars(select(Role)).all()

    def update_user_role(self, username, new_role):
        with self.Session() as session:
            user = session.get(User, username)
            role = session.get(Role, new_role)
            
            if not user or not role:
                return False, "Invalid user/role"
            
            user.role = new_role
            session.commit()
            return True, "Role updated"

    def delete_role(self, role_name):
        with self.Session() as session:
            role = session.get(Role, role_name)
            if not role:
                return False, "Role not found"
            
            if role_name in ['admin', 'user']:
                return False, "Cannot delete system roles"
            
            session.delete(role)
            session.commit()
            return True, "Role deleted"

    # User Management
    def get_all_users(self):
        """Retrieve all users with sanitized output (admin only)"""
        if st.session_state.get('role') != 'admin':
            st.error("Insufficient permissions")
            return []
        
        with self.Session() as session:
            users = session.query(User).all()
            return [
                {
                    "username": user.username,
                    "role": user.role,
                    "created_at": user.created_at,
                    "last_login": user.last_login,
                    "active": user.is_active
                }
                for user in users
            ]

    def delete_user(self, username):
        """Delete user account (admin only)"""
        if st.session_state.get('role') != 'admin':
            return False, "Insufficient permissions"
        
        with self.Session() as session:
            user = session.get(User, username)
            if not user:
                return False, "User not found"
            
            session.delete(user)
            session.commit()
            return True, "User deleted"

    # Session Management
    def is_authenticated(self):
        return st.session_state.authenticated

    def logout(self):
        st.session_state.clear()
        # st.rerun(scope="app")

    # UI Components
    def render_auth_ui(self):
        

        
        auth_tab, reg_tab = st.tabs(["Login", "Register"])
    
        with auth_tab:
            with st.form("Login"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                if st.form_submit_button("Login"):
                    if self.authenticate_user(username, password):
                        st.rerun()
                    else:
                        st.error("Invalid credentials")

        with reg_tab:
            with st.form("Register"):
                username = st.text_input("Choose username")
                password = st.text_input("Choose password", type="password")
                role_options = [r.name for r in self.get_all_roles()]
                role = st.selectbox("Role", role_options, 
                                  disabled=st.session_state.get('role') != 'admin')
                if st.form_submit_button("Register"):
                    success, message = self.register_user(username, password, role)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
        
        
        

    # Security Decorators
    def require_role(self, role):
        def decorator(func):
            def wrapper(*args, **kwargs):
                if st.session_state.get('role') != role:
                    st.error("Insufficient permissions")
                    return
                return func(*args, **kwargs)
            return wrapper
        return decorator
