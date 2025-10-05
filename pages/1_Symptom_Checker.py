import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ai.symptom_analyzer import analyze_symptoms, check_emergency, get_medicine_recommendations
from src.storage.local_db import add_health_record

st.set_page_config(page_title="Symptom Checker", page_icon="🩺", layout="wide")

st.title("🩺 AI Symptom Checker")

st.warning("""
⚠️ **IMPORTANT:** This is NOT a medical diagnosis tool. 
For serious symptoms, consult a healthcare professional immediately.
""")

# Symptom Input
st.subheader("Tell me about your symptoms")

col1, col2 = st.columns([2, 1])

with col1:
    symptoms = st.text_area(
        "Describe your symptoms",
        placeholder="E.g., I have a headache and fever since this morning. Temperature is 100°F.",
        height=150
    )

with col2:
    age = st.number_input("Age", min_value=1, max_value=120, value=30)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    duration = st.selectbox(
        "Duration",
        ["Less than 24 hours", "1-3 days", "3-7 days", "More than a week"]
    )

# Analyze Button
if st.button("🔍 Analyze Symptoms", type="primary", use_container_width=True):
    if not symptoms:
        st.error("Please describe your symptoms first!")
    else:
        # Emergency check
        if check_emergency(symptoms):
            st.error("🚨 MEDICAL EMERGENCY DETECTED!")
            st.markdown("""
            ### ⚠️ SEEK IMMEDIATE MEDICAL ATTENTION
            
            Your symptoms may indicate a serious medical condition.
            
            **DO THIS NOW:**
            - 🚑 Call emergency services (911 / 108)
            - 🏥 Go to the nearest emergency room
            - 📞 Contact your doctor immediately
            """)
            st.stop()
        
        # Analyze with AI
        with st.spinner("🤖 Analyzing your symptoms..."):
            analysis = analyze_symptoms(symptoms, age, gender)
        
        # Save to records
        record = {
            "type": "symptom_check",
            "symptoms": symptoms,
            "age": age,
            "gender": gender,
            "duration": duration,
            "severity": analysis.get('severity', 'unknown'),
            "analysis": analysis,
            "recommendations": analysis.get('recommendations', [])
        }
        add_health_record(record)
        
        # Display Results
        st.success("✅ Analysis Complete!")
        
        # Severity
        severity = analysis.get('severity', 'unknown')
        severity_colors = {'mild': '🟢', 'moderate': '🟡', 'severe': '🔴', 'unknown': '⚪'}
        
        st.markdown(f"### {severity_colors.get(severity, '⚪')} Severity: {severity.upper()}")
        
        # Disclaimer
        st.info(analysis.get('disclaimer', '⚠️ This is NOT a medical diagnosis.'))
        
        # Possible Conditions
        if analysis.get('possible_conditions'):
            st.subheader("🔍 Possible Conditions")
            for condition in analysis['possible_conditions']:
                prob = condition.get('probability', 'unknown')
                prob_emoji = {'low': '🔵', 'medium': '🟡', 'high': '🔴'}.get(prob, '⚪')
                
                with st.expander(f"{prob_emoji} {condition.get('name', 'Unknown')} - {prob.title()} Probability"):
                    st.write(condition.get('description', 'No description'))
        
        # Recommendations
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("✅ Recommendations")
            for rec in analysis.get('recommendations', []):
                st.success(f"• {rec}")
            
            if analysis.get('home_care'):
                st.subheader("🏠 Home Care")
                for tip in analysis['home_care']:
                    st.info(f"• {tip}")
        
        with col2:
            st.subheader("⚠️ Warning Signs")
            if analysis.get('red_flags'):
                for flag in analysis['red_flags']:
                    st.error(f"• {flag}")
            
            if analysis.get('see_doctor_if'):
                st.subheader("👨‍⚕️ See Doctor If:")
                for condition in analysis['see_doctor_if']:
                    st.warning(f"• {condition}")
        
        # Medicine Recommendations
        if analysis.get('otc_medicine_category'):
            st.markdown("---")
            st.subheader("💊 Suggested OTC Medicines")
            
            medicines = get_medicine_recommendations(analysis['otc_medicine_category'])
            
            if medicines:
                for med in medicines:
                    with st.expander(f"💊 {med['name']} ({', '.join(med['brands'])})"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Generic:** {med['generic']}")
                            st.write(f"**Use:** {med['use']}")
                            st.write(f"**Dosage:** {med['dosage']}")
                        
                        with col2:
                            st.write(f"**Price:** {med['price_range']}")
                            st.write("**Side Effects:**")
                            for effect in med['side_effects']:
                                st.write(f"- {effect}")
                        
                        st.warning("**Warnings:** " + ", ".join(med['warnings']))
                        
                        if st.button(f"🛒 Order {med['name']}", key=f"order_{med['name']}"):
                            st.session_state.medicine_to_order = med['name']
                            st.switch_page("pages/3_Order_Medicine.py")
        
        # Next Steps
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 View Records", use_container_width=True):
                st.switch_page("pages/4_Health_Records.py")
        
        with col2:
            if st.button("💊 Browse Medicines", use_container_width=True):
                st.switch_page("pages/2_Medicine_Guide.py")
        
        with col3:
            if st.button("🛒 Order Medicine", use_container_width=True):
                st.switch_page("pages/3_Order_Medicine.py")

# Symptom Guide
st.markdown("---")
st.subheader("📚 Common Symptoms Guide")

with st.expander("🤒 Fever"):
    st.write("""
    **When to worry:**
    - Temperature > 103°F (39.4°C)
    - Lasting more than 3 days
    
    **Home care:**
    - Stay hydrated
    - Rest
    - Take Paracetamol
    """)

with st.expander("🤧 Cold & Cough"):
    st.write("""
    **When to worry:**
    - Difficulty breathing
    - Chest pain
    - Lasting > 10 days
    
    **Home care:**
    - Drink warm fluids
    - Rest
    - Use humidifier
    """)

# Sidebar
with st.sidebar:
    st.header("💡 Tips")
    st.info("""
    **Be Specific:**
    - Describe exact symptoms
    - Include duration
    - Mention severity
    
    **Example:**
    "Throbbing headache on right side for 2 hours. Severity 7/10. Also nauseous."
    """)
    
    st.markdown("---")
    
    st.error("""
    **🚨 Emergency Symptoms:**
    - Chest pain
    - Difficulty breathing
    - Severe bleeding
    - Loss of consciousness
    """)