import os
from dotenv import load_dotenv

load_dotenv()

# Configuration constants
AI_API_KEY = os.getenv("AI_API_KEY")
DATABASE_PATH = "health_tracker.db"

# Supported languages
LANGUAGES = {
    'en': 'English',
    'es': 'Spanish', 
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'hi': 'Hindi',
    'zh': 'Chinese',
    'ja': 'Japanese'
}

# Triage levels
TRIAGE_LEVELS = {
    "self-monitor": "🟢 Self Monitor",
    "visit-doctor": "🟡 Visit Doctor", 
    "urgent-care": "🟠 Urgent Care",
    "emergency": "🔴 Emergency"
}