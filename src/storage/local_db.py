import json
import os
from datetime import datetime
from typing import List, Dict, Optional

DATA_DIR = "data"

def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def load_json(filename: str):
    ensure_data_dir()
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        return [] if filename not in ["symptom_rules.json", "medicine_database.json"] else {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return [] if filename not in ["symptom_rules.json", "medicine_database.json"] else {}

def save_json(filename: str, data):
    ensure_data_dir()
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Health Records
def add_health_record(record: Dict):
    records = load_json("health_records.json")
    record['id'] = f"rec_{len(records) + 1}_{int(datetime.now().timestamp())}"
    record['timestamp'] = datetime.now().isoformat()
    records.append(record)
    save_json("health_records.json", records)
    return record

def get_health_records() -> List[Dict]:
    return load_json("health_records.json")

def get_recent_records(limit: int = 10) -> List[Dict]:
    records = get_health_records()
    return sorted(records, key=lambda x: x.get('timestamp', ''), reverse=True)[:limit]

# Medicine Orders
def add_order(order: Dict):
    orders = load_json("orders.json")
    order['id'] = f"ord_{len(orders) + 1}_{int(datetime.now().timestamp())}"
    order['order_date'] = datetime.now().isoformat()
    order['status'] = 'pending'
    orders.append(order)
    save_json("orders.json", orders)
    return order

def get_orders() -> List[Dict]:
    return load_json("orders.json")

def update_order_status(order_id: str, status: str):
    orders = get_orders()
    for order in orders:
        if order['id'] == order_id:
            order['status'] = status
            order['updated_at'] = datetime.now().isoformat()
            break
    save_json("orders.json", orders)

# Reminders
def add_reminder(reminder: Dict):
    reminders = load_json("reminders.json")
    reminder['id'] = f"rem_{len(reminders) + 1}_{int(datetime.now().timestamp())}"
    reminder['created_at'] = datetime.now().isoformat()
    reminder['active'] = True
    reminders.append(reminder)
    save_json("reminders.json", reminders)
    return reminder

def get_active_reminders() -> List[Dict]:
    reminders = load_json("reminders.json")
    return [r for r in reminders if r.get('active', True)]

def deactivate_reminder(reminder_id: str):
    reminders = load_json("reminders.json")
    for reminder in reminders:
        if reminder['id'] == reminder_id:
            reminder['active'] = False
            break
    save_json("reminders.json", reminders)

# Medicine Database
def get_medicine_database() -> Dict:
    db = load_json("medicine_database.json")
    if not db:
        return initialize_medicine_database()
    return db

def initialize_medicine_database():
    medicines = {
        "pain_fever": [
            {
                "name": "Paracetamol",
                "generic": "Acetaminophen",
                "brands": ["Crocin", "Dolo", "Calpol"],
                "dosage": "500mg-1000mg every 4-6 hours",
                "max_daily": "4000mg",
                "use": "Pain relief, fever reduction",
                "side_effects": ["Rare: liver damage at high doses"],
                "warnings": ["Don't exceed maximum dose", "Avoid with alcohol"],
                "price_range": "₹10-₹30 per strip"
            },
            {
                "name": "Ibuprofen",
                "generic": "Ibuprofen",
                "brands": ["Brufen", "Advil", "Combiflam"],
                "dosage": "200mg-400mg every 4-6 hours",
                "max_daily": "1200mg (OTC)",
                "use": "Pain, inflammation, fever",
                "side_effects": ["Stomach upset", "Heartburn"],
                "warnings": ["Take with food", "Not for stomach ulcers"],
                "price_range": "₹15-₹40 per strip"
            }
        ],
        "cold_cough": [
            {
                "name": "Cetirizine",
                "generic": "Cetirizine",
                "brands": ["Zyrtec", "Alerid", "Cetrizet"],
                "dosage": "10mg once daily",
                "max_daily": "10mg",
                "use": "Allergic rhinitis, cold symptoms",
                "side_effects": ["Drowsiness", "Dry mouth"],
                "warnings": ["May cause drowsiness"],
                "price_range": "₹20-₹50 per strip"
            }
        ],
        "acidity": [
            {
                "name": "Omeprazole",
                "generic": "Omeprazole",
                "brands": ["Omez", "Prilosec"],
                "dosage": "20mg once daily before breakfast",
                "max_daily": "20mg (OTC)",
                "use": "Acid reflux, heartburn",
                "side_effects": ["Headache", "Nausea"],
                "warnings": ["Take 30 min before eating"],
                "price_range": "₹30-₹80 per strip"
            }
        ],
        "digestive": [
            {
                "name": "Loperamide",
                "generic": "Loperamide",
                "brands": ["Imodium", "Eldoper"],
                "dosage": "2mg initially, then 2mg after each loose stool",
                "max_daily": "8mg",
                "use": "Diarrhea",
                "side_effects": ["Constipation", "Dizziness"],
                "warnings": ["Don't use if fever present"],
                "price_range": "₹25-₹60 per strip"
            }
        ]
    }
    save_json("medicine_database.json", medicines)
    return medicines