import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import utils
from pathlib import Path

# Initialize
if 'orders_changed' not in st.session_state:
    st.session_state.orders_changed = False

# Create data directory and file if they don't exist
Path("data").mkdir(exist_ok=True)
if not Path("data/orders.csv").exists():
    utils.create_empty_orders_file()

st.title("Baker's Order Management System")

# Sidebar for adding new orders
st.sidebar.header("Add New Order")

# Order input form
with st.sidebar.form("new_order_form"):
    customer_name = st.text_input("Customer Name")
    order_details = st.text_area("Order Details")
    order_date = st.date_input("Order Date")
    delivery_date = st.date_input("Delivery Date")
    priority = st.selectbox("Priority", ["High", "Medium", "Low"])
    submitted = st.form_submit_button("Add Order")

    if submitted:
        if customer_name and order_details:
            utils.add_new_order(customer_name, order_details, order_date, delivery_date, priority)
            st.session_state.orders_changed = True
            st.success("Order added successfully!")
            st.rerun()
        else:
            st.error("Please fill in all required fields")

# Main content area
tab1, tab2, tab3 = st.tabs(["Daily Orders", "All Orders", "Reminders"])

with tab1:
    st.header("Today's Orders")
    today_orders = utils.get_todays_orders()
    if not today_orders.empty:
        for _, order in today_orders.iterrows():
            with st.expander(f"{order['customer_name']} - {order['order_details'][:50]}..."):
                st.write(f"**Delivery Date:** {order['delivery_date']}")
                st.write(f"**Priority:** {order['priority']}")
                st.write(f"**Status:** {order['status']}")
                new_status = st.selectbox(
                    "Update Status",
                    ["New", "In Progress", "Completed"],
                    index=["New", "In Progress", "Completed"].index(order['status']),
                    key=f"status_{order['id']}"
                )
                if new_status != order['status']:
                    utils.update_order_status(order['id'], new_status)
                    st.rerun()
    else:
        st.info("No orders for today")

with tab2:
    st.header("All Orders")
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.multiselect(
            "Filter by Status",
            ["New", "In Progress", "Completed"]
        )
    with col2:
        priority_filter = st.multiselect(
            "Filter by Priority",
            ["High", "Medium", "Low"]
        )

    search_term = st.text_input("Search Orders", "")
    
    # Get and display filtered orders
    orders = utils.get_filtered_orders(status_filter, priority_filter, search_term)

    if not orders.empty:
        # Display orders in an interactive way
        for _, order in orders.iterrows():
            with st.expander(f"{order['customer_name']} - {order['order_details'][:50]}..."):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Order Date:** {order['order_date']}")
                    st.write(f"**Delivery Date:** {order['delivery_date']}")
                    st.write(f"**Priority:** {order['priority']}")
                with col2:
                    st.write(f"**Current Status:** {order['status']}")
                    new_status = st.selectbox(
                        "Update Status",
                        ["New", "In Progress", "Completed"],
                        index=["New", "In Progress", "Completed"].index(order['status']),
                        key=f"all_status_{order['id']}"
                    )
                    if new_status != order['status']:
                        utils.update_order_status(order['id'], new_status)
                        st.success(f"Status updated to {new_status}")
                        st.rerun()
    else:
        st.info("No orders found")

with tab3:
    st.header("Upcoming Reminders")
    upcoming_orders = utils.get_upcoming_orders()
    
    if not upcoming_orders.empty:
        for _, order in upcoming_orders.iterrows():
            days_remaining = (pd.to_datetime(order['delivery_date']) - pd.Timestamp.now()).days
            
            if days_remaining <= 3:  # High priority reminder
                st.error(f"⚠️ URGENT: Order for {order['customer_name']} due in {days_remaining} days!")
            elif days_remaining <= 7:  # Medium priority reminder
                st.warning(f"📅 Upcoming: Order for {order['customer_name']} due in {days_remaining} days")
            else:  # Normal reminder
                st.info(f"ℹ️ Planned: Order for {order['customer_name']} due in {days_remaining} days")
    else:
        st.info("No upcoming orders")