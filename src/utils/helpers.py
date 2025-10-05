from datetime import datetime

def format_datetime(iso_string: str) -> str:
    """Format ISO datetime to readable format"""
    try:
        dt = datetime.fromisoformat(iso_string)
        return dt.strftime("%B %d, %Y at %I:%M %p")
    except:
        return iso_string

def get_severity_color(severity: str) -> str:
    """Get color for severity level"""
    colors = {
        'mild': '🟢',
        'moderate': '🟡',
        'severe': '🔴',
        'emergency': '🚨',
        'unknown': '⚪'
    }
    return colors.get(severity.lower(), '⚪')