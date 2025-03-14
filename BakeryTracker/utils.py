import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
from pathlib import Path
import os

ORDERS_FILE = "data/orders.csv"

def create_empty_orders_file():
    """Create an empty orders CSV file with the required columns."""
    df = pd.DataFrame(columns=[
        'id', 'customer_name', 'order_details', 'order_date', 
        'delivery_date', 'priority', 'status', 'created_at'
    ])
    df.to_csv(ORDERS_FILE, index=False)

def get_next_id():
    """Get the next available ID for a new order."""
    try:
        df = pd.read_csv(ORDERS_FILE)
        return 0 if df.empty else df['id'].max() + 1
    except:
        return 0

def add_new_order(customer_name, order_details, order_date, delivery_date, priority):
    """Add a new order to the CSV file."""
    try:
        df = pd.read_csv(ORDERS_FILE)
    except:
        create_empty_orders_file()
        df = pd.read_csv(ORDERS_FILE)
    
    new_order = {
        'id': get_next_id(),
        'customer_name': customer_name,
        'order_details': order_details,
        'order_date': order_date,
        'delivery_date': delivery_date,
        'priority': priority,
        'status': 'New',
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    df = pd.concat([df, pd.DataFrame([new_order])], ignore_index=True)
    df.to_csv(ORDERS_FILE, index=False)

def get_todays_orders():
    """Get all orders for today."""
    try:
        df = pd.read_csv(ORDERS_FILE)
        today = datetime.now().date()
        return df[pd.to_datetime(df['delivery_date']).dt.date == today]
    except:
        return pd.DataFrame()

def update_order_status(order_id, new_status):
    """Update the status of an order."""
    df = pd.read_csv(ORDERS_FILE)
    df.loc[df['id'] == order_id, 'status'] = new_status
    df.to_csv(ORDERS_FILE, index=False)

def get_filtered_orders(status_filter=None, priority_filter=None, search_term=""):
    """Get filtered orders based on status, priority, and search term."""
    try:
        df = pd.read_csv(ORDERS_FILE)
        
        if status_filter:
            df = df[df['status'].isin(status_filter)]
        
        if priority_filter:
            df = df[df['priority'].isin(priority_filter)]
        
        if search_term:
            search_condition = (
                df['customer_name'].str.contains(search_term, case=False, na=False) |
                df['order_details'].str.contains(search_term, case=False, na=False)
            )
            df = df[search_condition]
        
        return df
    except:
        return pd.DataFrame()

def get_upcoming_orders():
    """Get upcoming orders for reminders."""
    try:
        df = pd.read_csv(ORDERS_FILE)
        df['delivery_date'] = pd.to_datetime(df['delivery_date'])
        today = pd.Timestamp.now()
        
        # Get orders that are not completed and due within the next 14 days
        upcoming = df[
            (df['status'] != 'Completed') & 
            (df['delivery_date'] > today) & 
            (df['delivery_date'] <= today + timedelta(days=14))
        ]
        
        return upcoming.sort_values('delivery_date')
    except:
        return pd.DataFrame()
