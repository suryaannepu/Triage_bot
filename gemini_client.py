# 
import os
import json
import google.generativeai as genai
from config import AI_API_KEY

# Configure Gemini
genai.configure(api_key=AI_API_KEY)

# Global model instance for better performance
_model_instance = None

def setup_gemini_model():
    """Set up the Gemini model (singleton pattern for better performance)"""
    global _model_instance
    if _model_instance is not None:
        return _model_instance
    
    try:
        # Use gemini-2.0-flash for faster responses
        _model_instance = genai.GenerativeModel(
            'gemini-2.0-flash',
            generation_config={
                "temperature": 0.1,  # Lower temperature for more deterministic responses
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 1024,  # Limit tokens for faster responses
            }
        )
        return _model_instance
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
    
    prompt = f"""
As a medical triage assistant, analyze these symptoms and provide recommendations:
{symptoms}

Respond with a JSON object containing ONLY these fields:
- "triage_level": "self-monitor" or "visit-doctor"
- "confidence": "Low", "Medium", or "High"
- "reasoning": Brief explanation (1-2 sentences)
- "recommended_action": Concise next steps (1-2 sentences)
- "detailed_analysis": More detailed medical analysis (2-3 sentences)

Return ONLY valid JSON, no other text. Respond in the same language as the user's symptoms.
Keep responses concise and to the point.
"""
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean response text (remove markdown code blocks if present)
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        if response_text.startswith("json"):
            response_text = response_text[4:]
        
        return json.loads(response_text)
    except Exception as e:
        return {
            "triage_level": "self-monitor",
            "confidence": "Medium",
            "reasoning": f"Error in analysis",
            "recommended_action": "Please consult a healthcare professional",
            "detailed_analysis": "Unable to generate detailed analysis"
        }

def generate_chat_response(user_message: str, chat_history: list, language: str = 'en') -> str:
    """Generate conversational response from health assistant"""
    model = setup_gemini_model()
    if not model:
        return "I'm currently unavailable. Please try again later."
    
    # Format only the most recent 3 messages for faster processing
    history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history[-3:]])
    
    prompt = f"""
You are a warm and approachable health assistant.
Respond in the same language as the user's message. Keep responses concise (1-2 sentences max).

Recent conversation:
{history_text}

User: {user_message}

Assistant (brief response in user's language):
"""
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return "I'm having trouble responding right now. Please try again."

def generate_medical_report(user_profile: dict, health_logs: list, triage_history: list, language: str = 'en') -> str:
    """Generate a comprehensive medical report"""
    model = setup_gemini_model()
    if not model:
        return "Unable to generate report at this time. Please try again later."
    
    # Prepare minimal data for report generation
    profile_text = f"""
Name: {user_profile.get('full_name', 'Not provided')}
DOB: {user_profile.get('date_of_birth', 'Not provided')}
Blood: {user_profile.get('blood_group', 'Not provided')}
Allergies: {user_profile.get('allergies', 'None')}
Medications: {user_profile.get('medications', 'None')}
Conditions: {user_profile.get('chronic_conditions', 'None')}
"""
    
    # Use only last 5 logs for faster processing
    logs_text = "\n".join([f"{log['date']}: {log['symptoms'][:100]}{'...' if len(log['symptoms']) > 100 else ''}" 
                          for log in health_logs[-5:]])
    
    # Use only last 3 triage results
    triage_text = "\n".join([f"{result['created_at']}: {result['triage_level']}" 
                            for result in triage_history[-3:]])
    
    prompt = f"""
Create a brief medical report in the same language as the symptoms data.

PATIENT:
{profile_text}

RECENT SYMPTOMS (last 5):
{logs_text}

RECENT TRIAGE (last 3):
{triage_text}

Generate a very concise report with:
1. Summary (1 line)
2. Trends (1 line)
3. Patterns (1 line)
4. Risk (1 line)
5. Recommendations (1 line)

Keep it extremely brief and professional.
"""
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return "Error generating report. Please try again."

def detect_language(text: str) -> str:
    """Detect language from text using Gemini"""
    model = setup_gemini_model()
    if not model:
        return 'en'  # Default to English if model not available
    
    # Use shorter text sample for faster detection
    short_text = text[:200]  # Only use first 200 characters
    
    prompt = f"""
Detect language of this text. Return ONLY the language code (en, es, fr, etc.):
{short_text}

Language code:
"""
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip().lower()[:2]  # Only take first 2 chars
    except:
        return 'en'  # Default to English on error