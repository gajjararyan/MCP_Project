import streamlit as st
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.storage.local_db import add_reminder, get_active_reminders, deactivate_reminder

st.set_page_config(page_title="Reminders", page_icon="⏰", layout="wide")

st.title("⏰ Medication Reminders")

st.info("📱 Set reminders to never miss your medication!")

# Add Reminder
st.subheader("➕ Add Reminder")

with st.form("add_reminder"):
    col1, col2 = st.columns(2)
    
    with col1:
        medicine = st.text_input("Medicine", placeholder="E.g., Paracetamol 500mg")
        dosage = st.text_input("Dosage", placeholder="E.g., 1 tablet")
        frequency = st.selectbox(
            "Frequency",
            ["Once daily", "Twice daily", "Three times daily", "As needed"]
        )
    
    with col2:
        times = st.multiselect(
            "Times",
            ["6:00 AM", "8:00 AM", "9:00 AM", "12:00 PM", "2:00 PM", 
             "6:00 PM", "8:00 PM", "10:00 PM"],
            default=["9:00 AM"]
        )
        
        duration = st.number_input("Duration (days)", min_value=1, max_value=90, value=7)
        notes = st.text_area("Notes", placeholder="E.g., Take with food")
    
    if st.form_submit_button("✅ Set Reminder", use_container_width=True, type="primary"):
        if not medicine:
            st.error("Enter medicine name!")
        elif not times:
            st.error("Select at least one time!")
        else:
            reminder = {
                'medicine': medicine,
                'dosage': dosage,
                'frequency': frequency,
                'times': times,
                'duration_days': duration,
                'notes': notes,
                'start_date': datetime.now().isoformat()
            }
            
            add_reminder(reminder)
            st.success(f"✅ Reminder set for {medicine}!")
            st.balloons()
            st.rerun()

# Active Reminders
st.markdown("---")
st.subheader("📋 Active Reminders")

reminders = get_active_reminders()

if not reminders:
    st.info("No reminders yet. Add one above!")
else:
    for reminder in reminders:
        with st.expander(f"💊 {reminder.get('medicine')} - {reminder.get('frequency')}"):
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.write(f"**Medicine:** {reminder.get('medicine')}")
                st.write(f"**Dosage:** {reminder.get('dosage')}")
                st.write(f"**Frequency:** {reminder.get('frequency')}")
                if reminder.get('notes'):
                    st.info(f"📝 {reminder['notes']}")
            
            with col2:
                st.write("**Times:**")
                for t in reminder.get('times', []):
                    st.success(f"• {t}")
                st.write(f"**Duration:** {reminder.get('duration_days')} days")
            
            with col3:
                if st.button("✅ Taken", key=f"taken_{reminder.get('id')}", use_container_width=True):
                    st.success("Marked!")
                
                if st.button("🗑️ Delete", key=f"del_{reminder.get('id')}", use_container_width=True):
                    deactivate_reminder(reminder.get('id'))
                    st.rerun()

# Today's Schedule
st.markdown("---")
st.subheader("📅 Today's Schedule")

if reminders:
    schedule = {}
    for reminder in reminders:
        for time in reminder.get('times', []):
            if time not in schedule:
                schedule[time] = []
            schedule[time].append(reminder)
    
    for time in sorted(schedule.keys(), key=lambda x: datetime.strptime(x, "%I:%M %p")):
        st.markdown(f"### ⏰ {time}")
        for reminder in schedule[time]:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"💊 {reminder.get('medicine')} - {reminder.get('dosage')}")
            with col2:
                if st.button("✅ Done", key=f"done_{time}_{reminder.get('id')}"):
                    st.success("✓")
else:
    st.info("No schedule for today")

# Tips
st.markdown("---")
st.subheader("💡 Tips")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("""
    **Best Practices:**
    - Same time daily
    - Don't skip doses
    - Complete course
    """)

with col2:
    st.success("""
    **DO:**
    - Read labels
    - Follow advice
    - Track effects
    """)

with col3:
    st.error("""
    **DON'T:**
    - Double dose
    - Share meds
    - Stop suddenly
    """)

# Sidebar
with st.sidebar:
    st.header("⏰ Quick Add")
    
    if st.button("💊 Morning (8 AM)", use_container_width=True):
        st.info("Quick add for 8 AM")
    
    if st.button("💊 Evening (8 PM)", use_container_width=True):
        st.info("Quick add for 8 PM")
    
    st.markdown("---")
    
    st.metric("Active", len(reminders))
    
    st.markdown("---")
    
    st.info("""
    **Never Miss:**
    - Set multiple reminders
    - Enable notifications
    - Keep meds visible
    """)