def validate_age(age: int) -> bool:
    """Validate age input"""
    return 0 < age < 150

def validate_medicine_name(name: str) -> bool:
    """Validate medicine name"""
    return len(name.strip()) > 0

def sanitize_input(text: str) -> str:
    """Sanitize user input"""
    return text.strip()