from typing import Dict, List
import random
from datetime import datetime, timedelta

class PharmacyMCPServer:
    def __init__(self):
        self.pharmacies = self._initialize_pharmacies()
    
    def _initialize_pharmacies(self) -> List[Dict]:
        return [
            {
                "id": "ph_001",
                "name": "Apollo Pharmacy",
                "location": "Near You",
                "distance": "0.5 km",
                "rating": 4.5,
                "delivery_time": "15-20 min",
                "delivery_fee": 0
            },
            {
                "id": "ph_002",
                "name": "MedPlus",
                "location": "City Center",
                "distance": "1.2 km",
                "rating": 4.3,
                "delivery_time": "25-30 min",
                "delivery_fee": 20
            },
            {
                "id": "ph_003",
                "name": "1mg",
                "location": "Online",
                "distance": "N/A",
                "rating": 4.7,
                "delivery_time": "60-90 min",
                "delivery_fee": 0
            },
            {
                "id": "ph_004",
                "name": "PharmEasy",
                "location": "Online",
                "distance": "N/A",
                "rating": 4.6,
                "delivery_time": "2-4 hours",
                "delivery_fee": 0
            }
        ]
    
    def search_medicine(self, medicine_name: str) -> List[Dict]:
        results = []
        base_price = random.randint(50, 500)
        
        for pharmacy in self.pharmacies:
            price_variation = random.uniform(0.8, 1.2)
            price = int(base_price * price_variation)
            
            results.append({
                "pharmacy": pharmacy,
                "medicine_name": medicine_name,
                "price": price,
                "in_stock": random.choice([True, True, True, False]),
                "quantity_available": random.randint(5, 50),
                "discount": random.choice([0, 5, 10, 15])
            })
        
        return sorted(results, key=lambda x: x['price'])
    
    def place_order(self, medicine: str, pharmacy_id: str, quantity: int = 1) -> Dict:
        pharmacy = next((p for p in self.pharmacies if p['id'] == pharmacy_id), None)
        
        if not pharmacy:
            return {"error": "Pharmacy not found"}
        
        order = {
            "order_id": f"ORD{random.randint(10000, 99999)}",
            "medicine": medicine,
            "quantity": quantity,
            "pharmacy": pharmacy['name'],
            "delivery_time": pharmacy['delivery_time'],
            "delivery_fee": pharmacy['delivery_fee'],
            "status": "confirmed",
            "estimated_delivery": (datetime.now() + timedelta(hours=2)).strftime("%I:%M %p")
        }
        
        return order
    
    def track_order(self, order_id: str) -> Dict:
        statuses = ["Order Confirmed", "Pharmacy Preparing", "Out for Delivery", "Delivered"]
        current_status = random.choice(statuses)
        
        return {
            "order_id": order_id,
            "status": current_status,
            "last_updated": datetime.now().strftime("%I:%M %p"),
            "timeline": [
                {"status": "Order Confirmed", "time": "10:30 AM", "completed": True},
                {"status": "Pharmacy Preparing", "time": "10:45 AM", "completed": current_status != "Order Confirmed"},
                {"status": "Out for Delivery", "time": "11:15 AM", "completed": current_status in ["Out for Delivery", "Delivered"]},
                {"status": "Delivered", "time": "12:00 PM", "completed": current_status == "Delivered"}
            ]
        }
    
    def check_prescription_required(self, medicine_name: str) -> Dict:
        rx_keywords = ["antibiotic", "azithromycin", "amoxicillin", "steroid", "prednis"]
        requires_rx = any(keyword in medicine_name.lower() for keyword in rx_keywords)
        
        return {
            "medicine": medicine_name,
            "prescription_required": requires_rx,
            "category": "Prescription Medicine" if requires_rx else "Over-the-Counter (OTC)",
            "message": "Upload prescription to proceed" if requires_rx else "Can be ordered without prescription"
        }

pharmacy_mcp = PharmacyMCPServer()