import streamlit as st
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.storage.local_db import get_health_records

st.set_page_config(page_title="Health Records", page_icon="📊", layout="wide")

st.title("📊 Health Records")

records = get_health_records()

if not records:
    st.info("📝 No records yet! Check symptoms to create your first record.")
    if st.button("🩺 Check Symptoms"):
        st.switch_page("pages/1_Symptom_Checker.py")
    st.stop()

# Stats
st.subheader("📈 Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Records", len(records))

with col2:
    recent = [r for r in records if r.get('timestamp', '') >= (datetime.now() - timedelta(days=30)).isoformat()]
    st.metric("Last 30 Days", len(recent))

with col3:
    severe = len([r for r in records if r.get('severity') == 'severe'])
    st.metric("Severe Cases", severe)

with col4:
    mild = len([r for r in records if r.get('severity') == 'mild'])
    st.metric("Mild Cases", mild)

st.markdown("---")

# Filters
st.subheader("🔍 Filters")

col1, col2, col3 = st.columns(3)

with col1:
    time_filter = st.selectbox("Period", ["All Time", "Last 7 Days", "Last 30 Days"])

with col2:
    severity_filter = st.multiselect(
        "Severity",
        ["mild", "moderate", "severe"],
        default=["mild", "moderate", "severe"]
    )

with col3:
    search = st.text_input("Search", placeholder="Search symptoms...")

# Apply filters
filtered = records

if time_filter != "All Time":
    days = {"Last 7 Days": 7, "Last 30 Days": 30}[time_filter]
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    filtered = [r for r in filtered if r.get('timestamp', '') >= cutoff]

filtered = [r for r in filtered if r.get('severity') in severity_filter]

if search:
    filtered = [r for r in filtered if search.lower() in r.get('symptoms', '').lower()]

filtered = sorted(filtered, key=lambda x: x.get('timestamp', ''), reverse=True)

st.write(f"**Showing {len(filtered)} of {len(records)} records**")

# Display records
for record in filtered:
    severity = record.get('severity', 'unknown')
    colors = {'mild': '🟢', 'moderate': '🟡', 'severe': '🔴', 'unknown': '⚪'}
    
    timestamp = record.get('timestamp', '')
    if timestamp:
        date_str = datetime.fromisoformat(timestamp).strftime("%B %d, %Y at %I:%M %p")
    else:
        date_str = "Unknown"
    
    with st.expander(f"{colors.get(severity, '⚪')} {date_str} - {severity.title()}"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📝 Symptoms")
            st.write(record.get('symptoms', 'No symptoms'))
            
            if record.get('analysis', {}).get('recommendations'):
                st.markdown("### ✅ Recommendations")
                for rec in record['analysis']['recommendations'][:3]:
                    st.success(f"• {rec}")
        
        with col2:
            st.markdown("### ℹ️ Details")
            st.write(f"**Age:** {record.get('age', 'N/A')}")
            st.write(f"**Gender:** {record.get('gender', 'N/A')}")
            st.write(f"**Duration:** {record.get('duration', 'N/A')}")
            st.write(f"**Severity:** {severity.title()}")

# Export
st.markdown("---")
if st.button("📥 Export All Records"):
    import json
    st.download_button(
        "Download JSON",
        json.dumps(records, indent=2),
        f"health_records_{datetime.now().strftime('%Y%m%d')}.json",
        "application/json"
    )

# Sidebar
with st.sidebar:
    st.header("📊 Stats")
    
    if records:
        symptoms = ' '.join([r.get('symptoms', '') for r in records]).lower()
        common = ['headache', 'fever', 'pain', 'cough']
        
        st.subheader("Common Symptoms")
        for word in common:
            count = symptoms.count(word)
            if count > 0:
                st.write(f"• {word.title()}: {count}")
    
    st.markdown("---")
    
    st.info("""
    **Tips:**
    - Record promptly
    - Be specific
    - Track patterns
    - Share with doctor
    """)