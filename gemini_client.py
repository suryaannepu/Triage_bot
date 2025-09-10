import os
import json
import google.generativeai as genai
from config import AI_API_KEY

# Configure Gemini
genai.configure(api_key=AI_API_KEY)

def setup_gemini_model():
    """Set up the Gemini model"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model
    except Exception as e:
        print(f"Error setting up Gemini model: {e}")
        return None

def evaluate_health_score(symptoms_text: str) -> int:
    """Evaluate health score based on symptoms description"""
    model = setup_gemini_model()
    if not model:
        return 50  # Default if no model
    
    prompt = f"""
    Analyze these health symptoms and provide a severity score from 0 (perfect health) to 100 (critical condition):
    {symptoms_text}
    
    Return ONLY a single integer number, nothing else.
    """
    
    try:
        response = model.generate_content(prompt)
        return int(response.text.strip())
    except:
        return 50  # Default on error

def generate_triage_assessment(symptoms: str, language: str = 'en') -> dict:
    """Generate triage assessment using Gemini"""
    model = setup_gemini_model()
    if not model:
        return {
            "triage_level": "self-monitor",
            "confidence": "Medium",
            "reasoning": "System temporarily unavailable",
            "recommended_action": "Please try again later",
            "detailed_analysis": "Unable to generate analysis due to system error"
        }
    
    language_names = {
        'en': 'English', 'es': 'Spanish', 'fr': 'French', 'de': 'German',
        'it': 'Italian', 'pt': 'Portuguese', 'zh': 'Chinese', 'ja': 'Japanese',
        'hi': 'Hindi'
    }
    lang_name = language_names.get(language, 'English')
    
    prompt = f"""
    As a medical triage assistant, analyze these symptoms and provide recommendations in {lang_name}:
    {symptoms}
    
    Respond with a JSON object containing:
    - "triage_level": "self-monitor" or "visit-doctor"
    - "confidence": "Low", "Medium", or "High"
    - "reasoning": Brief explanation in {lang_name}
    - "recommended_action": Concise next steps in {lang_name}
    - "detailed_analysis": More detailed medical analysis in {lang_name}
    
    Return ONLY valid JSON, no other text.
    """
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean response text (remove markdown code blocks if present)
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        return json.loads(response_text)
    except Exception as e:
        return {
            "triage_level": "self-monitor",
            "confidence": "Medium",
            "reasoning": f"Error in analysis: {str(e)}",
            "recommended_action": "Please consult a healthcare professional",
            "detailed_analysis": "Unable to generate detailed analysis due to system error"
        }

def generate_chat_response(user_message: str, chat_history: list, language: str = 'en') -> str:
    """Generate conversational response from health assistant"""
    model = setup_gemini_model()
    if not model:
        return "I'm currently unavailable. Please try again later."
    
    # Format chat history
    history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history[-6:]])
    
    prompt = f"""
    You are a friendly, multilingual health assistant. Respond in {language} language.
    
    Previous conversation:
    {history_text}
    
    User: {user_message}
    
    Assistant: 
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"I'm having trouble responding right now. Error: {str(e)}"

def generate_medical_report(user_profile: dict, health_logs: list, triage_history: list) -> str:
    """Generate a comprehensive medical report"""
    model = setup_gemini_model()
    if not model:
        return "Unable to generate report at this time. Please try again later."
    
    # Prepare data for report generation
    profile_text = f"""
    Patient Profile:
    - Name: {user_profile.get('full_name', 'Not provided')}
    - Date of Birth: {user_profile.get('date_of_birth', 'Not provided')}
    - Blood Group: {user_profile.get('blood_group', 'Not provided')}
    - Height: {user_profile.get('height', 'Not provided')}
    - Weight: {user_profile.get('weight', 'Not provided')}
    - Allergies: {user_profile.get('allergies', 'None reported')}
    - Medications: {user_profile.get('medications', 'None reported')}
    - Chronic Conditions: {user_profile.get('chronic_conditions', 'None reported')}
    """
    
    logs_text = "\n".join([f"- {log['date']}: {log['symptoms']} (Score: {log.get('severity_score', 'N/A')})" 
                          for log in health_logs[:10]])  # Last 10 logs
    
    triage_text = "\n".join([f"- {result['created_at']}: {result['symptoms']} -> {result['triage_level']}" 
                            for result in triage_history[:5]])  # Last 5 triage results
    
    prompt = f"""
    You are a medical assistant that generates clear, structured, and professional medical reports for doctors.
    You will be given a patient profile (static details) and daily health logs (dynamic details).
    Your task: Combine this information into a concise yet complete medical report.
    Make it easy for a doctor to quickly understand the patient's condition, medical history, and trends.
    Do not add imaginary diseases or treatments. If information is missing, mention it clearly.
    Use keywords and keep it short.
    
    PATIENT PROFILE:
    {profile_text}
    
    RECENT HEALTH LOGS (last 10 entries):
    {logs_text}
    
    RECENT TRIAGE ASSESSMENTS (last 5 entries):
    {triage_text}
    
    Generate a concise medical report with these sections:
    1. Patient Summary (2-3 lines)
    2. Health Trend Analysis (3-4 lines)
    3. Symptom Patterns (2-3 lines)
    4. Risk Assessment (2 lines)
    5. Recommendations (2-3 lines)
    
    Keep it brief and professional.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating report: {str(e)}"

def detect_language(text: str) -> str:
    """Detect language from text"""
    # Simple language detection
    common_words = {
        'en': ['the', 'and', 'you', 'that', 'have'],
        'es': ['el', 'la', 'que', 'y', 'en'],
        'fr': ['le', 'la', 'et', 'les', 'des'],
        'de': ['der', 'die', 'das', 'und', 'ich'],
        'hi': ['मैं', 'तुम', 'वह', 'क्या', 'है'],
        'zh': ['的', '是', '在', '我', '有']
    }
    
    text_lower = text.lower()
    for lang, words in common_words.items():
        if any(word in text_lower for word in words):
            return lang
    return 'en'  # Default to English