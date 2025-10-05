import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.mcp.pharmacy_server import pharmacy_mcp
from src.storage.local_db import add_order, get_orders

st.set_page_config(page_title="Order Medicine", page_icon="🛒", layout="wide")

st.title("🛒 Order Medicine")

# Pre-fill if coming from other page
if 'medicine_to_order' in st.session_state:
    default_medicine = st.session_state.medicine_to_order
    del st.session_state.medicine_to_order
else:
    default_medicine = ""

# Search Medicine
st.subheader("🔍 Search Medicine")

medicine_name = st.text_input(
    "Medicine name",
    value=default_medicine,
    placeholder="E.g., Paracetamol, Crocin, Dolo 650"
)

quantity = st.number_input("Quantity", min_value=1, max_value=10, value=1)

# Search
if st.button("🔍 Search Pharmacies", type="primary", disabled=not medicine_name):
    with st.spinner("Searching..."):
        # Check prescription
        rx_check = pharmacy_mcp.check_prescription_required(medicine_name)
        
        st.markdown("---")
        
        if rx_check['prescription_required']:
            st.error(f"""
            ⚠️ **{rx_check['category']}**
            
            {rx_check['message']}
            """)
            
            uploaded_file = st.file_uploader("📸 Upload Prescription", type=['jpg', 'png', 'pdf'])
            
            if not uploaded_file:
                st.warning("Upload prescription to continue")
                st.stop()
            else:
                st.success("✅ Prescription uploaded!")
        else:
            st.success(f"✅ {rx_check['message']}")
        
        # Search pharmacies
        results = pharmacy_mcp.search_medicine(medicine_name)
        
        st.subheader(f"📍 Found {len(results)} Pharmacies")
        
        for idx, result in enumerate(results):
            pharmacy = result['pharmacy']
            
            if not result['in_stock']:
                continue
            
            col1, col2, col3 = st.columns([3, 2, 2])
            
            with col1:
                st.markdown(f"### {pharmacy['name']}")
                st.write(f"📍 {pharmacy['location']} ({pharmacy['distance']})")
                st.write(f"⭐ {pharmacy['rating']}/5")
            
            with col2:
                discount = result['discount']
                price = result['price']
                final_price = int(price * (1 - discount/100))
                
                if discount > 0:
                    st.markdown(f"~~₹{price}~~ **₹{final_price}**")
                    st.success(f"💰 Save {discount}%")
                else:
                    st.markdown(f"**₹{final_price}**")
                
                st.write(f"🚚 {pharmacy['delivery_time']}")
                if pharmacy['delivery_fee'] > 0:
                    st.write(f"Fee: ₹{pharmacy['delivery_fee']}")
                else:
                    st.success("✅ Free Delivery")
            
            with col3:
                total = final_price * quantity + pharmacy['delivery_fee']
                st.metric("Total", f"₹{total}")
                
                if st.button("🛒 Order", key=f"order_{idx}", use_container_width=True, type="primary"):
                    order_result = pharmacy_mcp.place_order(medicine_name, pharmacy['id'], quantity)
                    
                    order_data = {
                        'order_id': order_result['order_id'],
                        'medicine': medicine_name,
                        'quantity': quantity,
                        'pharmacy': pharmacy['name'],
                        'price': final_price,
                        'delivery_fee': pharmacy['delivery_fee'],
                        'total': total,
                        'delivery_time': pharmacy['delivery_time'],
                        'estimated_delivery': order_result['estimated_delivery']
                    }
                    
                    add_order(order_data)
                    
                    st.success(f"""
                    ✅ **Order Placed!**
                    
                    Order ID: {order_result['order_id']}
                    Delivery: {pharmacy['delivery_time']}
                    ETA: {order_result['estimated_delivery']}
                    """)
                    
                    st.balloons()
            
            st.markdown("---")

# Track Order
st.markdown("---")
st.subheader("📦 Track Order")

track_id = st.text_input("Order ID", placeholder="ORD12345")

if st.button("🔍 Track", disabled=not track_id):
    tracking = pharmacy_mcp.track_order(track_id)
    
    st.success(f"**Order:** {tracking['order_id']}")
    st.write(f"**Status:** {tracking['status']}")
    st.write(f"**Updated:** {tracking['last_updated']}")
    
    st.markdown("---")
    st.subheader("Timeline")
    
    for step in tracking['timeline']:
        if step['completed']:
            st.success(f"✅ {step['status']} - {step['time']}")
        else:
            st.info(f"⏳ {step['status']} - {step['time']}")

# Recent Orders
st.markdown("---")
st.subheader("📋 Recent Orders")

orders = get_orders()

if orders:
    for order in sorted(orders, key=lambda x: x.get('order_date', ''), reverse=True)[:5]:
        with st.expander(f"Order #{order.get('order_id', order.get('id', ''))[-6:]}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Medicine:** {order.get('medicine')}")
                st.write(f"**Pharmacy:** {order.get('pharmacy')}")
            
            with col2:
                st.write(f"**Total:** ₹{order.get('total')}")
                st.write(f"**Status:** {order.get('status', 'pending').title()}")
else:
    st.info("No orders yet!")

# Sidebar
with st.sidebar:
    st.header("❓ Help")
    
    st.subheader("📋 How to Order")
    st.write("""
    1. Enter medicine name
    2. Select quantity
    3. Click Search
    4. Compare prices
    5. Click Order
    6. Track delivery
    """)
    
    st.markdown("---")
    
    st.subheader("🚚 Delivery")
    st.info("""
    - 1-2 hour delivery
    - Free from select pharmacies
    - Real-time tracking
    - Contactless delivery
    """)