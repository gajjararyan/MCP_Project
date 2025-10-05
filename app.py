import streamlit as st
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from src.storage.local_db import get_health_records, get_orders, get_active_reminders

st.set_page_config(
    page_title="AI Health Copilot",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #EF4444 0%, #DC2626 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .stat-card {
        background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .warning-box {
        background-color: #FEF2F2;
        border-left: 4px solid #EF4444;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🏥 AI Health Copilot</h1>', unsafe_allow_html=True)
st.markdown("### Your Personal Health Assistant")

# Medical Disclaimer
st.markdown("""
<div class="warning-box">
    <h4>⚠️ MEDICAL DISCLAIMER</h4>
    <p><strong>This is NOT a substitute for professional medical advice.</strong></p>
    <p>Always consult with a qualified healthcare provider for medical advice, diagnosis, or treatment.</p>
    <p><strong>EMERGENCY:</strong> If you have chest pain, difficulty breathing, or severe symptoms, call emergency services immediately!</p>
</div>
""", unsafe_allow_html=True)

# Emergency Button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🚨 MEDICAL EMERGENCY - CALL 911/108", use_container_width=True, type="primary"):
        st.error("⚠️ For immediate medical emergency, call 911 (USA) or 108 (India)")

st.markdown("---")

# Load data
health_records = get_health_records()
orders = get_orders()
reminders = get_active_reminders()

# Stats
st.subheader("📊 Quick Stats")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="stat-card">
        <h2 style="margin:0;">{len(health_records)}</h2>
        <p style="margin:0;">Health Records</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="stat-card" style="background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);">
        <h2 style="margin:0;">{len(orders)}</h2>
        <p style="margin:0;">Medicine Orders</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="stat-card" style="background: linear-gradient(135deg, #10B981 0%, #059669 100%);">
        <h2 style="margin:0;">{len(reminders)}</h2>
        <p style="margin:0;">Active Reminders</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    pending = len([o for o in orders if o.get('status') == 'pending'])
    st.markdown(f"""
    <div class="stat-card" style="background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);">
        <h2 style="margin:0;">{pending}</h2>
        <p style="margin:0;">Pending Orders</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Quick Actions
st.subheader("⚡ Quick Actions")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("🩺 Check Symptoms", use_container_width=True):
        st.switch_page("pages/1_Symptom_Checker.py")

with col2:
    if st.button("💊 Browse Medicines", use_container_width=True):
        st.switch_page("pages/2_Medicine_Guide.py")

with col3:
    if st.button("🛒 Order Medicine", use_container_width=True):
        st.switch_page("pages/3_Order_Medicine.py")

with col4:
    if st.button("📊 View Records", use_container_width=True):
        st.switch_page("pages/4_Health_Records.py")

with col5:
    if st.button("⏰ Set Reminder", use_container_width=True):
        st.switch_page("pages/5_Reminders.py")

st.markdown("---")

# Recent Activity
col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 Recent Health Records")
    if health_records:
        recent = sorted(health_records, key=lambda x: x.get('timestamp', ''), reverse=True)[:5]
        for record in recent:
            with st.expander(f"Record - {record.get('timestamp', '')[:10]}"):
                st.write(f"**Symptoms:** {record.get('symptoms', 'N/A')}")
                st.write(f"**Severity:** {record.get('severity', 'N/A')}")
    else:
        st.info("No health records yet. Start by checking your symptoms!")

with col2:
    st.subheader("📦 Recent Orders")
    if orders:
        recent_orders = sorted(orders, key=lambda x: x.get('order_date', ''), reverse=True)[:5]
        for order in recent_orders:
            with st.expander(f"Order #{order.get('id', 'N/A')[-6:]}"):
                st.write(f"**Medicine:** {order.get('medicine', 'N/A')}")
                st.write(f"**Status:** {order.get('status', 'N/A').title()}")
    else:
        st.info("No orders yet!")

# Health Tips
st.markdown("---")
st.subheader("💡 Health Tips")

import random
tips = [
    "💧 Drink 8 glasses of water daily",
    "🏃 Exercise 30 minutes, 5 days a week",
    "😴 Get 7-8 hours of sleep",
    "🥗 Eat fruits and vegetables",
]

cols = st.columns(4)
for idx, tip in enumerate(tips):
    with cols[idx]:
        st.success(tip)

# Sidebar
with st.sidebar:
    st.header("ℹ️ About")
    st.write("""
    **AI Health Copilot** helps you:
    - 🩺 Analyze symptoms
    - 💊 Find OTC medicines
    - 🛒 Order from pharmacies
    - 📊 Track health history
    - ⏰ Set medication reminders
    """)
    
    st.markdown("---")
    
    st.error("""
    **⚠️ When to See a Doctor:**
    - Chest pain
    - Difficulty breathing
    - High fever (>103°F)
    - Severe pain
    """)