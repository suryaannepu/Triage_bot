import sqlite3
import bcrypt
from datetime import datetime, date, timedelta  # Added timedelta import
from typing import List, Dict, Any, Optional

def create_user(email: str, password: str, full_name: str) -> int:
    """Create a new user with hashed password"""
    conn = sqlite3.connect('health_tracker.db')
    c = conn.cursor()
    
    # Hash password
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    created_at = datetime.now().isoformat()
    
    try:
        c.execute('''INSERT INTO users (email, password_hash, full_name, created_at, last_login)
                     VALUES (?, ?, ?, ?, ?)''',
                 (email, password_hash, full_name, created_at, created_at))
        user_id = c.lastrowid
        conn.commit()
        return user_id
    except sqlite3.IntegrityError:
        return -1  # User already exists
    finally:
        conn.close()

def authenticate_user(email: str, password: str) -> Optional[int]:
    """Authenticate user and return user ID if successful"""
    conn = sqlite3.connect('health_tracker.db')
    c = conn.cursor()
    
    c.execute('SELECT id, password_hash FROM users WHERE email = ?', (email,))
    result = c.fetchone()
    conn.close()
    
    if result and bcrypt.checkpw(password.encode('utf-8'), result[1].encode('utf-8')):
        return result[0]
    return None

def update_user_profile(user_id: int, profile_data: Dict[str, Any]) -> bool:
    """Update user profile information"""
    conn = sqlite3.connect('health_tracker.db')
    c = conn.cursor()
    
    try:
        c.execute('''UPDATE users 
                     SET full_name = ?, date_of_birth = ?, blood_group = ?, 
                         height = ?, weight = ?, allergies = ?, medications = ?,
                         chronic_conditions = ?, emergency_contact = ?
                     WHERE id = ?''',
                 (profile_data.get('full_name'), profile_data.get('date_of_birth'),
                  profile_data.get('blood_group'), profile_data.get('height'),
                  profile_data.get('weight'), profile_data.get('allergies'),
                  profile_data.get('medications'), profile_data.get('chronic_conditions'),
                  profile_data.get('emergency_contact'), user_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating profile: {e}")
        return False
    finally:
        conn.close()

def get_user_profile(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user profile information"""
    conn = sqlite3.connect('health_tracker.db')
    c = conn.cursor()
    
    c.execute('''SELECT email, full_name, date_of_birth, blood_group, height, weight, 
                        allergies, medications, chronic_conditions, emergency_contact
                 FROM users WHERE id = ?''', (user_id,))
    result = c.fetchone()
    conn.close()
    
    if result:
        return {
            'email': result[0],
            'full_name': result[1],
            'date_of_birth': result[2],
            'blood_group': result[3],
            'height': result[4],
            'weight': result[5],
            'allergies': result[6],
            'medications': result[7],
            'chronic_conditions': result[8],
            'emergency_contact': result[9]
        }
    return None

def add_health_log(user_id: int, symptoms: str, notes: str = "", severity_score: int = None) -> int:
    """Add a new health log entry"""
    conn = sqlite3.connect('health_tracker.db')
    c = conn.cursor()
    
    today = date.today().isoformat()
    created_at = datetime.now().isoformat()
    
    c.execute('''INSERT INTO health_logs (user_id, date, symptoms, severity_score, notes, created_at)
                 VALUES (?, ?, ?, ?, ?, ?)''',
             (user_id, today, symptoms, severity_score, notes, created_at))
    log_id = c.lastrowid
    
    # Update daily streak
    c.execute('''INSERT OR REPLACE INTO daily_streaks (user_id, date, completed, created_at)
                 VALUES (?, ?, 1, ?)''',
             (user_id, today, created_at))
    
    conn.commit()
    conn.close()
    return log_id

def get_health_logs(user_id: int, limit: int = 30) -> List[Dict[str, Any]]:
    """Get health logs for a user"""
    conn = sqlite3.connect('health_tracker.db')
    c = conn.cursor()
    
    c.execute('''SELECT id, date, symptoms, severity_score, notes, created_at
                 FROM health_logs 
                 WHERE user_id = ? 
                 ORDER BY date DESC 
                 LIMIT ?''', (user_id, limit))
    
    logs = []
    for row in c.fetchall():
        logs.append({
            'id': row[0],
            'date': row[1],
            'symptoms': row[2],
            'severity_score': row[3],
            'notes': row[4],
            'created_at': row[5]
        })
    
    conn.close()
    return logs

def add_triage_result(user_id: int, symptoms: str, triage_level: str, 
                     confidence: str, reasoning: str, recommended_action: str, 
                     detailed_analysis: str) -> int:
    """Add a triage result"""
    conn = sqlite3.connect('health_tracker.db')
    c = conn.cursor()
    
    created_at = datetime.now().isoformat()
    
    c.execute('''INSERT INTO triage_results 
                 (user_id, symptoms, triage_level, confidence, reasoning, 
                  recommended_action, detailed_analysis, created_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
             (user_id, symptoms, triage_level, confidence, reasoning, 
              recommended_action, detailed_analysis, created_at))
    
    result_id = c.lastrowid
    conn.commit()
    conn.close()
    return result_id

def get_triage_history(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """Get triage history for a user"""
    conn = sqlite3.connect('health_tracker.db')
    c = conn.cursor()
    
    c.execute('''SELECT id, symptoms, triage_level, confidence, reasoning, 
                        recommended_action, created_at
                 FROM triage_results 
                 WHERE user_id = ? 
                 ORDER BY created_at DESC 
                 LIMIT ?''', (user_id, limit))
    
    history = []
    for row in c.fetchall():
        history.append({
            'id': row[0],
            'symptoms': row[1],
            'triage_level': row[2],
            'confidence': row[3],
            'reasoning': row[4],
            'recommended_action': row[5],
            'created_at': row[6]
        })
    
    conn.close()
    return history

def get_streak_data(user_id: int) -> Dict[str, Any]:
    """Get user's streak information"""
    conn = sqlite3.connect('health_tracker.db')
    c = conn.cursor()
    
    # Get current streak
    c.execute('''SELECT date FROM daily_streaks 
                 WHERE user_id = ? AND completed = 1 
                 ORDER BY date DESC''', (user_id,))
    
    streaks = [row[0] for row in c.fetchall()]
    
    # Calculate current streak
    current_streak = 0
    today = date.today()
    
    for i, streak_date in enumerate(streaks):
        expected_date = (today - timedelta(days=i)).isoformat()
        if streak_date == expected_date:
            current_streak += 1
        else:
            break
    
    # Get longest streak
    # This query might need adjustment for SQLite
    # Let's use a simpler approach
    longest_streak = 0
    current = 0
    prev_date = None
    
    for streak_date in sorted(streaks):
        current_date = datetime.strptime(streak_date, '%Y-%m-%d').date()
        if prev_date and (current_date - prev_date).days == 1:
            current += 1
        else:
            current = 1
        longest_streak = max(longest_streak, current)
        prev_date = current_date
    
    conn.close()
    
    return {
        'current_streak': current_streak,
        'longest_streak': longest_streak or current_streak,
        'total_logs': len(streaks)
    }

def create_chat_session(user_id: int, session_type: str = "general") -> int:
    """Create a new chat session"""
    conn = sqlite3.connect('health_tracker.db')
    c = conn.cursor()
    
    created_at = datetime.now().isoformat()
    
    c.execute('INSERT INTO chat_sessions (user_id, session_type, created_at) VALUES (?, ?, ?)',
             (user_id, session_type, created_at))
    
    session_id = c.lastrowid
    conn.commit()
    conn.close()
    return session_id

def add_chat_message(session_id: int, role: str, content: str) -> int:
    """Add a message to a chat session"""
    conn = sqlite3.connect('health_tracker.db')
    c = conn.cursor()
    
    timestamp = datetime.now().isoformat()
    
    c.execute('INSERT INTO chat_messages (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)',
             (session_id, role, content, timestamp))
    
    message_id = c.lastrowid
    conn.commit()
    conn.close()
    return message_id

def get_chat_history(session_id: int) -> List[Dict[str, Any]]:
    """Get chat history for a session"""
    conn = sqlite3.connect('health_tracker.db')
    c = conn.cursor()
    
    c.execute('''SELECT role, content, timestamp 
                 FROM chat_messages 
                 WHERE session_id = ? 
                 ORDER BY timestamp ASC''', (session_id,))
    
    history = []
    for row in c.fetchall():
        history.append({
            'role': row[0],
            'content': row[1],
            'timestamp': row[2]
        })
    
    conn.close()
    return history