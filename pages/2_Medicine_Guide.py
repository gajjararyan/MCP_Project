import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.storage.local_db import get_medicine_database

st.set_page_config(page_title="Medicine Guide", page_icon="💊", layout="wide")

st.title("💊 OTC Medicine Guide")

st.info("ℹ️ Information about common over-the-counter medicines. Always read labels and consult a pharmacist if unsure.")

# Load database
db = get_medicine_database()

# Search
search = st.text_input("🔍 Search medicines", placeholder="Search by name or symptom...")

# Category filter
categories = list(db.keys())
category_names = {
    "pain_fever": "💊 Pain & Fever",
    "cold_cough": "🤧 Cold & Cough",
    "acidity": "🔥 Acidity",
    "digestive": "🏥 Digestive"
}

selected_category = st.selectbox(
    "Category",
    ["All"] + categories,
    format_func=lambda x: category_names.get(x, x.title()) if x != "All" else "All Categories"
)

# Get medicines
medicines = []
if selected_category == "All":
    for category in db.values():
        medicines.extend(category)
else:
    medicines = db.get(selected_category, [])

# Search filter
if search:
    search_lower = search.lower()
    medicines = [
        med for med in medicines
        if search_lower in med['name'].lower() 
        or search_lower in med['use'].lower()
        or any(search_lower in brand.lower() for brand in med['brands'])
    ]

st.write(f"**Showing {len(medicines)} medicines**")

# Display medicines
for med in medicines:
    with st.expander(f"💊 **{med['name']}** - {med['generic']}"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"### {med['name']}")
            st.write(f"**Generic:** {med['generic']}")
            st.write(f"**Brands:** {', '.join(med['brands'])}")
            
            st.markdown("---")
            st.write(f"**💡 Used For:** {med['use']}")
            
            st.markdown("---")
            st.markdown("#### 💊 Dosage")
            st.success(f"**Recommended:** {med['dosage']}")
            st.warning(f"**Max Daily:** {med['max_daily']}")
            
            st.markdown("---")
            st.markdown("#### ⚠️ Side Effects")
            for effect in med['side_effects']:
                st.write(f"- {effect}")
            
            st.markdown("---")
            st.markdown("#### 🚨 Warnings")
            for warning in med['warnings']:
                st.error(f"⚠️ {warning}")
        
        with col2:
            st.markdown("### 💰 Price")
            st.info(med['price_range'])
            
            st.markdown("---")
            
            if st.button(f"🛒 Order", key=f"order_{med['name']}", use_container_width=True):
                st.session_state.medicine_to_order = med['name']
                st.switch_page("pages/3_Order_Medicine.py")

# Safety Tips
st.markdown("---")
st.subheader("🛡️ Medicine Safety")

col1, col2, col3 = st.columns(3)

with col1:
    st.success("""
    **✅ DO:**
    - Read labels
    - Follow dosage
    - Check expiry
    - Store properly
    """)

with col2:
    st.error("""
    **❌ DON'T:**
    - Exceed dose
    - Mix with alcohol
    - Share medicines
    - Use expired
    """)

with col3:
    st.warning("""
    **⚠️ CAUTION:**
    - Pregnant/nursing
    - Children
    - Allergies
    - Drug interactions
    """)

# Sidebar
with st.sidebar:
    st.header("📖 Quick Reference")
    
    st.subheader("🤒 Fever & Pain")
    st.write("• Paracetamol")
    st.write("• Ibuprofen")
    
    st.subheader("🤧 Cold")
    st.write("• Cetirizine")
    
    st.subheader("🔥 Acidity")
    st.write("• Omeprazole")
    
    st.markdown("---")
    
    st.error("""
    **⚠️ Consult Doctor If:**
    - Symptoms worsen
    - No improvement in 3 days
    - Severe side effects
    """)