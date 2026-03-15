import streamlit as st

#st.set_page_config(page_title="Smart Coffee Kiosk Application")
st.title("Smart Coffee Kiosk Application")

import streamlit as st
import json
from pathlib import Path
import uuid

st.set_page_config(page_title="Smart Coffee Kiosk", page_icon="☕", layout="wide")

inventory_file = Path("inventory.json")
orders_file = Path("orders.json")

default_inventory = [
    {"id": 1, "name": "Espresso", "price": 2.50, "stock": 40},
    {"id": 2, "name": "Latte", "price": 4.25, "stock": 25},
    {"id": 3, "name": "Cold Brew", "price": 3.75, "stock": 30},
    {"id": 4, "name": "Mocha", "price": 4.50, "stock": 20},
    {"id": 5, "name": "Blueberry Muffin", "price": 2.95, "stock": 18}
]

def load_json(file_path, default_data):
    if file_path.exists():
        with open(file_path, "r") as f:
            return json.load(f)
    else:
        with open(file_path, "w") as f:
            json.dump(default_data, f, indent=4)
        return default_data

def save_json(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

def get_item_by_name(inventory, item_name):
    for item in inventory:
        if item["name"] == item_name:
            return item
    return None

inventory = load_json(inventory_file, default_inventory)
orders = load_json(orders_file, [])

st.title("☕ Smart Coffee Kiosk Dashboard")

tab1, tab2, tab3, tab4 = st.tabs([
    "Place Order",
    "View Inventory",
    "Restock",
    "Manage Orders"
])

with tab1:
    st.header("Place Order")

    item_names = [item["name"] for item in inventory]

    with st.form("place_order_form"):
        selected_item_name = st.selectbox("Select Item", item_names)
        quantity = st.number_input("Quantity", min_value=1, step=1)
        customer_name = st.text_input("Customer Name")
        submit_order = st.form_submit_button("Place Order")

    if submit_order:
        selected_item = get_item_by_name(inventory, selected_item_name)

        if not customer_name.strip():
            st.error("Please enter a customer name.")
        elif selected_item["stock"] < quantity:
            st.error("Out of Stock")
        else:
            selected_item["stock"] -= quantity
            total_price = selected_item["price"] * quantity
            order_id = str(uuid.uuid4())[:8]

            new_order = {
                "order_id": order_id,
                "customer": customer_name,
                "item": selected_item_name,
                "quantity": quantity,
                "total": round(total_price, 2),
                "status": "Placed"
            }

            orders.append(new_order)

            save_json(inventory_file, inventory)
            save_json(orders_file, orders)

            st.success("Order Placed Successfully!")

            with st.expander("View Receipt"):
                st.write(f"Order ID: {order_id}")
                st.write(f"Customer: {customer_name}")
                st.write(f"Item: {selected_item_name}")
                st.write(f"Quantity: {quantity}")
                st.write(f"Total: ${total_price:.2f}")
                st.write("Status: Placed")

with tab2:
    st.header("View Inventory")

    search_term = st.text_input("Search by item name")
    total_stock = sum(item["stock"] for item in inventory)
    st.metric("Total Items in Stock", total_stock)

    filtered_inventory = [
        item for item in inventory
        if search_term.lower() in item["name"].lower()
    ]

    if filtered_inventory:
        for item in filtered_inventory:
            if item["stock"] < 10:
                st.warning(f"{item['name']} | Price: ${item['price']:.2f} | Stock: {item['stock']}")
            else:
                st.write(f"{item['name']} | Price: ${item['price']:.2f} | Stock: {item['stock']}")
    else:
        st.info("No items match your search.")

with tab3:
    st.header("Restock Inventory")

    restock_item_name = st.selectbox("Select Item to Restock", item_names)
    added_stock = st.number_input("Add Stock Amount", min_value=1, step=1)

    if st.button("Update Stock"):
        restock_item = get_item_by_name(inventory, restock_item_name)
        restock_item["stock"] += added_stock
        save_json(inventory_file, inventory)
        st.success(f"{restock_item_name} restocked successfully.")

with tab4:
    st.header("Manage Orders")

    active_orders = [order for order in orders if order["status"] == "Placed"]

    if active_orders:
        for order in active_orders:
            st.write(
                f"Order ID: {order['order_id']} | "
                f"Customer: {order['customer']} | "
                f"Item: {order['item']} | "
                f"Quantity: {order['quantity']} | "
                f"Total: ${order['total']:.2f}"
            )

        order_options = [f"{order['order_id']} - {order['customer']} ({order['item']})" for order in active_orders]
        selected_order_display = st.selectbox("Select Order to Cancel", order_options)

        if st.button("Cancel Order"):
            selected_order_id = selected_order_display.split(" - ")[0]

            for order in orders:
                if order["order_id"] == selected_order_id and order["status"] == "Placed":
                    order["status"] = "Cancelled"
                    refunded_item = get_item_by_name(inventory, order["item"])
                    if refunded_item:
                        refunded_item["stock"] += order["quantity"]

                    save_json(inventory_file, inventory)
                    save_json(orders_file, orders)

                    st.success("Order Cancelled and Stock Refunded")
                    st.rerun()
    else:
        st.info("No active orders to manage.")