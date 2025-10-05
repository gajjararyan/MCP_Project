import os
from dotenv import load_dotenv
import json
import re

load_dotenv()

# Try to import Gemini
try:
    import google.generativeai as genai
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key and api_key != 'your_gemini_key_here':
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        GEMINI_AVAILABLE = True
        print("✅ Gemini AI connected")
    else:
        GEMINI_AVAILABLE = False
        print("⚠️ Gemini API key not configured - using fallback")
except Exception as e:
    GEMINI_AVAILABLE = False
    print(f"⚠️ Gemini not available: {e}")

# Enhanced emergency keywords
EMERGENCY_KEYWORDS = [
    "chest pain", "heart attack", "can't breathe", "difficulty breathing", 
    "severe bleeding", "heavy bleeding", "unconscious", "passed out",
    "seizure", "convulsion", "stroke", "face drooping", "arm weakness",
    "severe headache", "worst headache", "blurred vision", "double vision",
    "severe abdominal pain", "stomach pain severe", "coughing blood", 
    "vomiting blood", "suicidal", "want to die", "kill myself",
    "severe burn", "choking", "poisoning", "overdose"
]

def extract_temperature(text: str) -> float:
    """Extract temperature from text"""
    text_lower = text.lower()
    
    # Patterns to match temperature
    patterns = [
        r'(\d+\.?\d*)\s*°?f',  # 100F, 100°F, 100.5F
        r'(\d+\.?\d*)\s*degree',  # 100 degree
        r'temperature\s+(?:is\s+)?(\d+\.?\d*)',  # temperature is 100
        r'fever\s+(?:of\s+)?(\d+\.?\d*)',  # fever of 100
        r'(?:above|over|more than)\s+(\d+\.?\d*)',  # above 100
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            try:
                temp = float(match.group(1))
                # If temp seems to be in Celsius (likely <50), convert to Fahrenheit
                if temp < 50 and temp > 35:
                    temp = (temp * 9/5) + 32
                return temp
            except:
                continue
    
    return None

def assess_fever_severity(temperature: float) -> dict:
    """Assess fever severity based on temperature"""
    if temperature >= 105:  # Critical
        return {
            "severity": "EMERGENCY",
            "message": "🚨 CRITICAL FEVER - IMMEDIATE MEDICAL ATTENTION REQUIRED!",
            "is_emergency": True,
            "reason": f"Fever of {temperature}°F is dangerously high and can cause brain damage"
        }
    elif temperature >= 103:  # Severe
        return {
            "severity": "severe",
            "message": "⚠️ HIGH FEVER - See doctor immediately",
            "is_emergency": False,
            "reason": f"Fever of {temperature}°F requires urgent medical evaluation"
        }
    elif temperature >= 101:  # Moderate
        return {
            "severity": "moderate",
            "message": "Moderate fever - Monitor closely",
            "is_emergency": False,
            "reason": f"Fever of {temperature}°F should be monitored"
        }
    elif temperature >= 99.5:  # Mild
        return {
            "severity": "mild",
            "message": "Mild fever",
            "is_emergency": False,
            "reason": f"Fever of {temperature}°F is mild"
        }
    else:
        return {
            "severity": "mild",
            "message": "Low-grade or no fever",
            "is_emergency": False,
            "reason": "Temperature is normal or slightly elevated"
        }

def detect_severity_indicators(text: str) -> str:
    """Detect severity from text indicators"""
    text_lower = text.lower()
    
    # Check for severity keywords
    if any(word in text_lower for word in ["unbearable", "worst", "extreme", "excruciating", "10/10", "9/10"]):
        return "severe"
    elif any(word in text_lower for word in ["severe", "bad", "intense", "terrible", "7/10", "8/10"]):
        return "severe"
    elif any(word in text_lower for word in ["moderate", "painful", "5/10", "6/10"]):
        return "moderate"
    else:
        return "mild"

def check_emergency(symptoms: str) -> bool:
    """Enhanced emergency detection with temperature checking"""
    symptoms_lower = symptoms.lower()
    
    # Check temperature first
    temp = extract_temperature(symptoms)
    if temp and temp >= 105:
        return True
    
    # Check for emergency keywords
    for keyword in EMERGENCY_KEYWORDS:
        if keyword in symptoms_lower:
            return True
    
    # Check for severe pain indicators
    if "severe" in symptoms_lower and any(word in symptoms_lower for word in ["pain", "bleeding", "headache"]):
        return True
    
    # Check for numeric severity
    if any(word in symptoms_lower for word in ["10/10", "9/10", "unbearable", "worst"]):
        return True
    
    return False

def detect_symptom_category(symptoms: str) -> str:
    """Detect symptom category"""
    symptoms_lower = symptoms.lower()
    
    # Fever category if temperature mentioned
    temp = extract_temperature(symptoms)
    if temp:
        return "pain_fever"
    
    # Keywords for each category
    categories = {
        "pain_fever": ["headache", "head pain", "fever", "temperature", "body pain", 
                       "body ache", "muscle pain", "joint pain", "back pain", "migraine"],
        "cold_cough": ["cold", "cough", "sneeze", "runny nose", "stuffy nose", 
                      "sore throat", "throat pain", "congestion", "phlegm"],
        "acidity": ["acidity", "heartburn", "acid reflux", "burning chest", 
                   "sour taste", "indigestion", "bloating", "gas"],
        "digestive": ["diarrhea", "loose motion", "stomach pain", "stomach ache",
                     "nausea", "vomiting", "constipation", "cramping"],
        "skin": ["rash", "itching", "skin rash", "allergy", "hives", 
                "red spots", "swelling", "skin irritation"]
    }
    
    # Count matches
    scores = {}
    for category, keywords in categories.items():
        score = sum(1 for keyword in keywords if keyword in symptoms_lower)
        if score > 0:
            scores[category] = score
    
    return max(scores, key=scores.get) if scores else None

def get_enhanced_analysis(symptoms: str, age: int = None) -> dict:
    """Enhanced fallback analysis with temperature awareness"""
    symptoms_lower = symptoms.lower()
    
    # Extract temperature
    temp = extract_temperature(symptoms)
    
    # Assess fever severity if temperature found
    fever_assessment = None
    if temp:
        fever_assessment = assess_fever_severity(temp)
        
        # If critical fever, return emergency
        if fever_assessment["is_emergency"]:
            return {
                "emergency": True,
                "severity": "EMERGENCY",
                "message": fever_assessment["message"],
                "temperature": temp,
                "possible_conditions": [
                    {
                        "name": "Hyperpyrexia (Extremely High Fever)",
                        "probability": "high",
                        "description": f"Fever of {temp}°F is a medical emergency. Can cause seizures, brain damage, or organ failure."
                    }
                ],
                "recommendations": [
                    "🚨 GO TO EMERGENCY ROOM IMMEDIATELY",
                    "DO NOT WAIT - This is life-threatening",
                    "Call 911/108 if unable to transport",
                    "Cool body with wet towels while getting to hospital"
                ],
                "red_flags": [
                    f"Fever of {temp}°F is critically dangerous",
                    "Risk of seizures and brain damage",
                    "Immediate medical intervention required"
                ],
                "disclaimer": "🚨 MEDICAL EMERGENCY - Seek immediate professional help!"
            }
    
    # Detect general severity
    severity_from_text = detect_severity_indicators(symptoms)
    
    # Determine final severity (use worse of the two)
    if fever_assessment:
        if fever_assessment["severity"] == "severe" or severity_from_text == "severe":
            final_severity = "severe"
        elif fever_assessment["severity"] == "moderate" or severity_from_text == "moderate":
            final_severity = "moderate"
        else:
            final_severity = fever_assessment["severity"]
    else:
        final_severity = severity_from_text
    
    # Detect category
    category = detect_symptom_category(symptoms)
    
    # Build response based on category
    if category == "pain_fever":
        conditions = [
            {
                "name": "Viral Fever" if temp and temp < 102 else "High Fever (Possible Infection)",
                "probability": "high" if temp and temp >= 102 else "medium",
                "description": f"Fever of {temp}°F with headache. " if temp else "" + 
                              "Common in viral infections. Needs medical evaluation if high or persistent."
            }
        ]
        
        # Adjust recommendations based on temperature
        if temp and temp >= 103:
            recommendations = [
                "🚨 SEE A DOCTOR IMMEDIATELY - Fever is too high",
                "Take Paracetamol 500mg ONLY if doctor not available soon",
                "Cool body with wet towels",
                "Drink plenty of water",
                "Do NOT delay medical care"
            ]
            red_flags = [
                f"Fever of {temp}°F requires urgent medical attention",
                "High risk of complications",
                "May need IV fluids or antibiotics"
            ]
        else:
            recommendations = [
                "Take Paracetamol 500mg for fever and pain relief",
                "Rest and stay hydrated",
                "Use cold compress on forehead",
                "Monitor temperature every 4 hours",
                "See doctor if fever lasts >3 days or worsens"
            ]
            red_flags = [
                "Fever above 103°F",
                "Fever lasting more than 3 days",
                "Severe headache with stiff neck",
                "Confusion or extreme drowsiness"
            ]
        
        return {
            "emergency": False,
            "severity": final_severity,
            "temperature": temp,
            "temperature_status": fever_assessment["message"] if fever_assessment else None,
            "possible_conditions": conditions,
            "recommendations": recommendations,
            "red_flags": red_flags,
            "home_care": [
                "Drink 8-10 glasses of water daily",
                "Rest in cool, comfortable environment",
                "Wear light clothing",
                "Take lukewarm bath if fever is high"
            ],
            "see_doctor_if": [
                "Fever above 103°F",
                "Fever lasts more than 3 days",
                "Severe headache or body pain",
                "Difficulty breathing",
                "Persistent vomiting"
            ],
            "otc_medicine_category": "pain_fever",
            "disclaimer": "⚠️ This is NOT a medical diagnosis. Consult a doctor for proper medical advice."
        }
    
    elif category == "cold_cough":
        return {
            "emergency": False,
            "severity": final_severity,
            "possible_conditions": [
                {
                    "name": "Common Cold",
                    "probability": "high",
                    "description": "Viral upper respiratory infection. Usually self-limiting in 7-10 days."
                }
            ],
            "recommendations": [
                "Take Cetirizine 10mg once daily",
                "Gargle with warm salt water",
                "Use steam inhalation",
                "Stay hydrated with warm fluids"
            ],
            "red_flags": [
                "Difficulty breathing",
                "Chest pain",
                "Coughing up blood",
                "Symptoms lasting >10 days"
            ],
            "home_care": [
                "Drink warm tea with honey",
                "Use humidifier",
                "Rest adequately",
                "Avoid cold beverages"
            ],
            "see_doctor_if": [
                "Breathing difficulty",
                "High fever develops",
                "Symptoms worsen after a week"
            ],
            "otc_medicine_category": "cold_cough",
            "disclaimer": "⚠️ This is NOT a medical diagnosis."
        }
    
    elif category == "acidity":
        return {
            "emergency": False,
            "severity": final_severity,
            "possible_conditions": [
                {
                    "name": "Acid Reflux (GERD)",
                    "probability": "high",
                    "description": "Stomach acid backing up into esophagus causing burning sensation."
                }
            ],
            "recommendations": [
                "Take Omeprazole 20mg before breakfast",
                "Avoid spicy and oily foods",
                "Eat smaller meals",
                "Don't lie down right after eating"
            ],
            "red_flags": [
                "Severe chest pain (could be heart-related)",
                "Difficulty swallowing",
                "Vomiting blood",
                "Black stools"
            ],
            "home_care": [
                "Drink cold milk",
                "Eat banana",
                "Avoid late-night meals",
                "Elevate head while sleeping"
            ],
            "see_doctor_if": [
                "Severe chest pain",
                "Symptoms persist despite medication",
                "Weight loss"
            ],
            "otc_medicine_category": "acidity",
            "disclaimer": "⚠️ This is NOT a medical diagnosis."
        }
    
    elif category == "digestive":
        return {
            "emergency": False,
            "severity": final_severity,
            "possible_conditions": [
                {
                    "name": "Gastroenteritis",
                    "probability": "high",
                    "description": "Stomach flu causing diarrhea and stomach upset."
                }
            ],
            "recommendations": [
                "Take ORS (Oral Rehydration Solution)",
                "Take Loperamide 2mg if needed",
                "Eat bland foods (rice, banana)",
                "Avoid dairy and spicy foods"
            ],
            "red_flags": [
                "Severe dehydration (dark urine, dizziness)",
                "Blood in stool",
                "High fever",
                "Severe abdominal pain"
            ],
            "home_care": [
                "Drink plenty of fluids",
                "BRAT diet",
                "Rest",
                "Maintain hygiene"
            ],
            "see_doctor_if": [
                "Symptoms last >2 days",
                "Severe dehydration",
                "Blood in vomit or stool"
            ],
            "otc_medicine_category": "digestive",
            "disclaimer": "⚠️ This is NOT a medical diagnosis."
        }
    
    # Generic response
    return {
        "emergency": False,
        "severity": final_severity,
        "possible_conditions": [
            {
                "name": "Requires Medical Evaluation",
                "probability": "unknown",
                "description": "Symptoms require professional assessment."
            }
        ],
        "recommendations": [
            "Consult a healthcare provider",
            "Monitor symptoms",
            "Keep track of any changes",
            "Stay hydrated and rest"
        ],
        "red_flags": [
            "Symptoms worsen",
            "New symptoms develop",
            "Severe pain"
        ],
        "home_care": [
            "Rest adequately",
            "Stay hydrated",
            "Monitor condition"
        ],
        "see_doctor_if": [
            "Symptoms persist",
            "You're concerned",
            "Symptoms worsen"
        ],
        "otc_medicine_category": None,
        "disclaimer": "⚠️ This is NOT a medical diagnosis."
    }

def analyze_symptoms(symptoms: str, age: int = None, gender: str = None) -> dict:
    """Main analysis function with enhanced temperature detection"""
    
    # Emergency check
    if check_emergency(symptoms):
        temp = extract_temperature(symptoms)
        temp_msg = f" (Temperature: {temp}°F)" if temp and temp >= 105 else ""
        
        return {
            "emergency": True,
            "severity": "EMERGENCY",
            "temperature": temp,
            "message": f"⚠️ MEDICAL EMERGENCY DETECTED{temp_msg}",
            "action": "Call emergency services (911/108) immediately or go to nearest ER",
            "possible_conditions": [],
            "recommendations": [
                "🚨 DO NOT DELAY - This is a medical emergency",
                "Call 911/108 NOW",
                "Go to nearest emergency room immediately",
                "If unable to transport, call ambulance"
            ],
            "disclaimer": "🚨 MEDICAL EMERGENCY - Professional help required immediately."
        }
    
    # Try AI first
    if GEMINI_AVAILABLE:
        try:
            temp = extract_temperature(symptoms)
            temp_context = f"IMPORTANT: Patient reports temperature of {temp}°F. " if temp else ""
            
            context = temp_context
            if age:
                context += f"Patient age: {age} years. "
            if gender:
                context += f"Gender: {gender}. "
            
            prompt = f"""You are a medical AI assistant. Analyze these symptoms carefully.

{context}
Symptoms: {symptoms}

CRITICAL: If temperature is mentioned and is above 103°F, classify as SEVERE.
If temperature is above 105°F, classify as EMERGENCY.

Provide analysis in EXACT JSON format (no markdown, just pure JSON):
{{
  "emergency": false,
  "severity": "mild" | "moderate" | "severe",
  "possible_conditions": [
    {{
      "name": "condition name",
      "probability": "low" | "medium" | "high",
      "description": "detailed description"
    }}
  ],
  "recommendations": ["specific recommendation 1", "recommendation 2", "recommendation 3", "recommendation 4"],
  "red_flags": ["warning sign 1", "warning sign 2", "warning sign 3"],
  "home_care": ["home care tip 1", "tip 2", "tip 3"],
  "see_doctor_if": ["condition 1", "condition 2", "condition 3"],
  "otc_medicine_category": "pain_fever" | "cold_cough" | "acidity" | "digestive" | null
}}"""

            response = model.generate_content(prompt)
            text = response.text.strip()
            text = text.replace('```json', '').replace('```', '').strip()
            
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_text = text[json_start:json_end]
                analysis = json.loads(json_text)
                
                # Override severity if high temperature detected
                temp = extract_temperature(symptoms)
                if temp:
                    fever_check = assess_fever_severity(temp)
                    if fever_check["severity"] == "severe" and analysis.get("severity") == "mild":
                        analysis["severity"] = "severe"
                    analysis["temperature"] = temp
                    analysis["temperature_status"] = fever_check["message"]
                
                analysis['disclaimer'] = "⚠️ This is NOT a medical diagnosis. Consult a doctor for proper medical advice."
                print("✅ AI analysis successful")
                return analysis
                
        except Exception as e:
            print(f"⚠️ AI error: {e}, using enhanced fallback")
    
    # Use enhanced fallback
    return get_enhanced_analysis(symptoms, age)

def get_medicine_recommendations(symptom_category: str) -> list:
    """Get medicine recommendations"""
    from src.storage.local_db import get_medicine_database
    db = get_medicine_database()
    return db.get(symptom_category, [])