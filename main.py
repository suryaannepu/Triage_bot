import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import time

# Import our modules
from database import (
    create_user, authenticate_user, update_user_profile, get_user_profile,
    add_health_log, get_health_logs, add_triage_result, get_triage_history,
    get_streak_data, create_chat_session, add_chat_message, get_chat_history
)
from gemini_client import (
    evaluate_health_score, generate_triage_assessment, 
    generate_chat_response, detect_language
)
from visualization import (
    create_health_trends_chart, create_streak_visualization,
    create_triage_distribution_chart, create_daily_patterns_chart
)
from report_generator import generate_pdf_report, export_health_data
from config import LANGUAGES, TRIAGE_LEVELS

# Page configuration
st.set_page_config(
    page_title="Health Tracker",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .streak-card {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .triage-card {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .self-monitor {
        border-left: 4px solid #28a745;
        background-color: #f8fff9;
    }
    .visit-doctor {
        border-left: 4px solid #ffc107;
        background-color: #fffef0;
    }
    .urgent-care {
        border-left: 4px solid #fd7e14;
        background-color: #fff5eb;
    }
    .emergency {
        border-left: 4px solid #dc3545;
        background-color: #fff5f5;
    }
    # .chat-message {
    #     padding: 1rem;
    #     border-radius: 0.5rem;
    #     margin-bottom: 0.5rem;
    # }
    # .user-message {
    #     background-color: #e6f7ff;
    #     margin-left: 20%;
    # }
    # .assistant-message {
    #     background-color: #f0f0f0;
    #     margin-right: 20%;
    # }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = "login"
if 'chat_session_id' not in st.session_state:
    st.session_state.chat_session_id = None
if 'language' not in st.session_state:
    st.session_state.language = 'en'

# Authentication functions
def show_login_page():
    st.title("Health Tracker Login")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            st.subheader("Login to Your Account")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")
            
            if login_button:
                user_id = authenticate_user(email, password)
                if user_id:
                    st.session_state.user_id = user_id
                    st.session_state.current_page = "dashboard"
                    st.rerun()
                else:
                    st.error("Invalid email or password")
        
        st.markdown("---")
        st.markdown("Don't have an account?")
        if st.button("Create Account"):
            st.session_state.current_page = "register"
            st.rerun()

def show_register_page():
    st.title("Create New Account")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("register_form"):
            st.subheader("Register New Account")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            full_name = st.text_input("Full Name")
            register_button = st.form_submit_button("Create Account")
            
            if register_button:
                if password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    user_id = create_user(email, password, full_name)
                    if user_id > 0:
                        st.session_state.user_id = user_id
                        st.session_state.current_page = "profile"
                        st.rerun()
                    else:
                        st.error("Email already exists")
        
        st.markdown("---")
        if st.button("Back to Login"):
            st.session_state.current_page = "login"
            st.rerun()

# Main application pages
def show_dashboard():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "Daily Check-in", "Symptom Triage", 
                                    "Health Assistant", "Health Trends", "Medical Reports", "Profile"])
    
    if page == "Dashboard":
        show_dashboard_content()
    elif page == "Daily Check-in":
        show_daily_checkin()
    elif page == "Symptom Triage":
        show_symptom_triage()
    elif page == "Health Assistant":
        show_health_assistant()
    elif page == "Health Trends":
        show_health_trends()
    elif page == "Medical Reports":
        show_medical_reports()
    elif page == "Profile":
        show_profile_page()
    
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout"):
        st.session_state.user_id = None
        st.session_state.current_page = "login"
        st.rerun()

def show_dashboard_content():
    st.markdown('<h1 class="main-header">🏥 Health Tracker Dashboard</h1>', unsafe_allow_html=True)
    
    # Get user data
    streak_data = get_streak_data(st.session_state.user_id)
    health_logs = get_health_logs(st.session_state.user_id, 7)  # Last 7 days
    triage_history = get_triage_history(st.session_state.user_id, 5)  # Last 5 triage results
    
    # Display streak information
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Current Streak", f"{streak_data['current_streak']} days")
    with col2:
        st.metric("Longest Streak", f"{streak_data['longest_streak']} days")
    with col3:
        st.metric("Total Entries", streak_data['total_logs'])
    
    st.markdown("---")
    
    # Recent health logs
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Recent Health Logs")
        if health_logs:
            for log in health_logs[:3]:  # Show last 3 logs
                with st.expander(f"{log['date']} - Score: {log.get('severity_score', 'N/A')}"):
                    st.write(f"**Symptoms:** {log['symptoms']}")
                    if log.get('notes'):
                        st.write(f"**Notes:** {log['notes']}")
        else:
            st.info("No health logs yet. Complete your daily check-in to get started.")
    
    with col2:
        st.subheader("Recent Triage Assessments")
        if triage_history:
            for triage in triage_history[:3]:  # Show last 3 triage results
                triage_class = triage['triage_level'].replace("-", "_")
                st.markdown(f'<div class="triage-card {triage_class}">'
                           f'<strong>{triage["created_at"][:10]}</strong><br>'
                           f'<strong>Symptoms:</strong> {triage["symptoms"][:50]}...<br>'
                           f'<strong>Assessment:</strong> {TRIAGE_LEVELS.get(triage["triage_level"], triage["triage_level"])} '
                           f'({triage["confidence"]} confidence)'
                           '</div>', unsafe_allow_html=True)
        else:
            st.info("No triage assessments yet. Use the Symptom Triage tool to get started.")
    
    # Quick actions
    st.markdown("---")
    st.subheader("Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Daily Check-in", use_container_width=True):
            st.session_state.current_page = "Daily Check-in"
            st.rerun()
    
    with col2:
        if st.button("🔍 Symptom Triage", use_container_width=True):
            st.session_state.current_page = "Symptom Triage"
            st.rerun()
    
    with col3:
        if st.button("💬 Health Assistant", use_container_width=True):
            st.session_state.current_page = "Health Assistant"
            st.rerun()

def show_daily_checkin():
    st.title("📝 Daily Health Check-in")
    
    # Check if already completed today
    today = date.today().isoformat()
    health_logs = get_health_logs(st.session_state.user_id, 1)
    already_completed = health_logs and health_logs[0]['date'] == today
    
    if already_completed:
        st.success("You've already completed your daily check-in today!")
        st.write(f"**Symptoms:** {health_logs[0]['symptoms']}")
        if health_logs[0].get('notes'):
            st.write(f"**Notes:** {health_logs[0]['notes']}")
        st.write(f"**Severity Score:** {health_logs[0].get('severity_score', 'N/A')}/100")
        
        if st.button("Update Today's Entry"):
            # Implement update functionality
            pass
    else:
        with st.form("daily_checkin_form"):
            symptoms = st.text_area("How are you feeling today? Describe any symptoms or concerns:", 
                                  height=100, 
                                  placeholder="e.g., Headache, fatigue, cough...")
            
            notes = st.text_area("Additional notes (optional):", 
                               height=60, 
                               placeholder="Any additional information about your health today...")
            
            submitted = st.form_submit_button("Submit Daily Check-in")
            
            if submitted and symptoms:
                # Evaluate health score
                severity_score = evaluate_health_score(symptoms)
                
                # Add to database
                add_health_log(st.session_state.user_id, symptoms, notes, severity_score)
                
                st.success("Daily check-in completed!")
                st.balloons()
                
                # Show results
                st.subheader("Today's Health Assessment")
                st.metric("Severity Score", f"{severity_score}/100")
                
                if severity_score < 30:
                    st.success("Your health appears to be good today!")
                elif severity_score < 70:
                    st.warning("You're experiencing some health concerns. Consider monitoring your symptoms.")
                else:
                    st.error("Your symptoms seem significant. Consider using our Symptom Triage tool or consulting a healthcare professional.")
                
                time.sleep(2)
                st.session_state.current_page = "dashboard"
                st.rerun()

def show_symptom_triage():
    st.title("🔍 Symptom Triage Assessment")
    
    st.info("Describe your symptoms in detail for a medical assessment. This tool uses AI to provide triage recommendations but is not a substitute for professional medical advice.")
    
    with st.form("triage_form"):
        symptoms = st.text_area("Describe your symptoms in detail:", 
                              height=120,
                              placeholder="e.g., I've had a persistent headache for 3 days, accompanied by nausea and sensitivity to light...")
        
        submitted = st.form_submit_button("Analyze Symptoms")
        
        if submitted and symptoms:
            with st.spinner("Analyzing symptoms..."):
                # Detect language
                language = detect_language(symptoms)
                
                # Generate triage assessment
                assessment = generate_triage_assessment(symptoms, language)
                
                # Save to database
                add_triage_result(
                    st.session_state.user_id, 
                    symptoms, 
                    assessment['triage_level'],
                    assessment['confidence'],
                    assessment['reasoning'],
                    assessment['recommended_action'],
                    assessment.get('detailed_analysis', '')
                )
                
                # Display results
                st.subheader("Triage Assessment")
                
                # Style based on triage level
                triage_class = assessment['triage_level'].replace("-", "_")
                st.markdown(f'<div class="triage-card {triage_class}">'
                           f'<h3>{TRIAGE_LEVELS.get(assessment["triage_level"], assessment["triage_level"])}</h3>'
                           f'<p><strong>Confidence:</strong> {assessment["confidence"]}</p>'
                           f'<p><strong>Reasoning:</strong> {assessment["reasoning"]}</p>'
                           f'<p><strong>Recommended Action:</strong> {assessment["recommended_action"]}</p>'
                           '</div>', unsafe_allow_html=True)
                
                if 'detailed_analysis' in assessment and assessment['detailed_analysis']:
                    with st.expander("Detailed Medical Analysis"):
                        st.write(assessment['detailed_analysis'])
                
                # Option to start a chat about these symptoms
                st.markdown("---")
                st.write("Would you like to discuss these symptoms with our health assistant?")
                if st.button("Chat with Health Assistant about these symptoms"):
                    # Create a new chat session with the symptoms as context
                    if not st.session_state.chat_session_id:
                        st.session_state.chat_session_id = create_chat_session(st.session_state.user_id)
                    
                    # Add symptoms as first message
                    add_chat_message(st.session_state.chat_session_id, "user", 
                                   f"I'm experiencing these symptoms: {symptoms}")
                    
                    # Generate initial response
                    chat_history = get_chat_history(st.session_state.chat_session_id)
                    response = generate_chat_response(
                        f"I'm experiencing these symptoms: {symptoms}", 
                        chat_history,
                        language
                    )
                    
                    add_chat_message(st.session_state.chat_session_id, "assistant", response)
                    
                    st.session_state.current_page = "Health Assistant"
                    st.rerun()

def show_health_assistant():
    st.title("💬 Health Assistant")
    
    # Initialize chat session if needed
    if not st.session_state.chat_session_id:
        st.session_state.chat_session_id = create_chat_session(st.session_state.user_id)
    
    # Get chat history
    chat_history = get_chat_history(st.session_state.chat_session_id)
    
    # Display chat history
    st.subheader("Conversation History")
    
    if not chat_history:
        st.info("Start a conversation with our health assistant. You can ask questions about symptoms, medications, general health advice, and more.")
    else:
        for message in chat_history:
            if message['role'] == 'user':
                st.markdown(f'<div class="chat-message user-message">'
                           f'<strong>You:</strong> {message["content"]}'
                           '</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message assistant-message">'
                           f'<strong>Assistant:</strong> {message["content"]}'
                           '</div>', unsafe_allow_html=True)
    
    # Chat input
    st.markdown("---")
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Add user message to chat
        add_chat_message(st.session_state.chat_session_id, "user", user_input)
        
        # Generate response
        with st.spinner("Health assistant is thinking..."):
            language = detect_language(user_input)
            response = generate_chat_response(user_input, chat_history, language)
            
            # Add assistant response to chat
            add_chat_message(st.session_state.chat_session_id, "assistant", response)
            
            # Rerun to update the chat display
            st.rerun()

def show_health_trends():
    st.title("📊 Health Trends & Analytics")
    
    # Get health data
    health_logs = get_health_logs(st.session_state.user_id, 365)  # Last year
    triage_history = get_triage_history(st.session_state.user_id, 100)  # Last 100 triage results
    
    # Time filter
    time_filter = st.selectbox("Time Range", ["Last 7 days", "Last 30 days", "Last 90 days", "Last year", "All time"])
    
    # Filter data based on selection
    if time_filter == "Last 7 days":
        cutoff_date = (datetime.now() - timedelta(days=7)).date().isoformat()
    elif time_filter == "Last 30 days":
        cutoff_date = (datetime.now() - timedelta(days=30)).date().isoformat()
    elif time_filter == "Last 90 days":
        cutoff_date = (datetime.now() - timedelta(days=90)).date().isoformat()
    elif time_filter == "Last year":
        cutoff_date = (datetime.now() - timedelta(days=365)).date().isoformat()
    else:  # All time
        cutoff_date = "2000-01-01"  # Arbitrary early date
    
    filtered_logs = [log for log in health_logs if log['date'] >= cutoff_date]
    
    # Display charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(create_health_trends_chart(filtered_logs), use_container_width=True)
    
    with col2:
        st.plotly_chart(create_streak_visualization(get_streak_data(st.session_state.user_id)), 
                       use_container_width=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.plotly_chart(create_triage_distribution_chart(triage_history), 
                       use_container_width=True)
    
    with col4:
        st.plotly_chart(create_daily_patterns_chart(health_logs), 
                       use_container_width=True)
    
    # Data table
    st.subheader("Raw Health Data")
    if health_logs:
        df = pd.DataFrame(health_logs)
        st.dataframe(df[['date', 'symptoms', 'severity_score', 'notes']], 
                    use_container_width=True)
    else:
        st.info("No health data available yet.")

def show_medical_reports():
    st.title("📋 Medical Reports & Export")
    
    st.info("Generate comprehensive medical reports or export your health data for sharing with healthcare providers.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Generate Medical Report")
        
        start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30))
        end_date = st.date_input("End Date", value=datetime.now())
        
        if st.button("Generate PDF Report"):
            with st.spinner("Generating report..."):
                report_data = generate_pdf_report(
                    st.session_state.user_id, 
                    start_date.isoformat(), 
                    end_date.isoformat()
                )
                
                if isinstance(report_data, bytes):
                    st.download_button(
                        label="Download PDF Report",
                        data=report_data,
                        file_name=f"health_report_{start_date}_{end_date}.pdf",
                        mime="application/pdf"
                    )
                else:
                    # Fallback: show HTML content
                    with st.expander("View Report Content"):
                        st.components.v1.html(report_data, height=600, scrolling=True)
    
    with col2:
        st.subheader("Export Health Data")
        
        export_format = st.selectbox("Export Format", ["CSV", "JSON"])
        
        if st.button(f"Export as {export_format}"):
            data = export_health_data(st.session_state.user_id, export_format.lower())
            
            st.download_button(
                label=f"Download {export_format}",
                data=data,
                file_name=f"health_data_export.{export_format.lower()}",
                mime="text/csv" if export_format.lower() == "csv" else "application/json"
            )
    
    # Recent reports section
    st.markdown("---")
    st.subheader("Report History")
    
    triage_history = get_triage_history(st.session_state.user_id, 10)
    if triage_history:
        for triage in triage_history:
            with st.expander(f"Triage Assessment - {triage['created_at'][:10]}"):
                st.write(f"**Symptoms:** {triage['symptoms']}")
                st.write(f"**Triage Level:** {triage['triage_level']} ({triage['confidence']} confidence)")
                st.write(f"**Reasoning:** {triage['reasoning']}")
                st.write(f"**Recommended Action:** {triage['recommended_action']}")
    else:
        st.info("No triage assessments available for reports.")

def show_profile_page():
    st.title("👤 User Profile")
    
    # Get current profile
    profile = get_user_profile(st.session_state.user_id)
    
    with st.form("profile_form"):
        st.subheader("Personal Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            email = st.text_input("Email", value=profile.get('email', ''), disabled=True)
            full_name = st.text_input("Full Name", value=profile.get('full_name', ''))
            date_of_birth = st.date_input("Date of Birth", 
                                         value=datetime.strptime(profile['date_of_birth'], '%Y-%m-%d').date() 
                                         if profile.get('date_of_birth') else None,
                                         max_value=datetime.now().date())
            blood_group = st.selectbox("Blood Group", 
                                      ["", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
                                      index=0 if not profile.get('blood_group') 
                                      else ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"].index(profile['blood_group']) + 1)
        
        with col2:
            height = st.number_input("Height (cm)", min_value=0.0, value=profile.get('height', 0.0) or 0.0)
            weight = st.number_input("Weight (kg)", min_value=0.0, value=profile.get('weight', 0.0) or 0.0)
            allergies = st.text_area("Allergies", value=profile.get('allergies', ''))
            medications = st.text_area("Current Medications", value=profile.get('medications', ''))
        
        chronic_conditions = st.text_area("Chronic Conditions", value=profile.get('chronic_conditions', ''))
        emergency_contact = st.text_area("Emergency Contact Information", value=profile.get('emergency_contact', ''))
        
        submitted = st.form_submit_button("Update Profile")
        
        if submitted:
            profile_data = {
                'full_name': full_name,
                'date_of_birth': date_of_birth.isoformat() if date_of_birth else None,
                'blood_group': blood_group,
                'height': height,
                'weight': weight,
                'allergies': allergies,
                'medications': medications,
                'chronic_conditions': chronic_conditions,
                'emergency_contact': emergency_contact
            }
            
            if update_user_profile(st.session_state.user_id, profile_data):
                st.success("Profile updated successfully!")
            else:
                st.error("Error updating profile")

# Main app logic
# def main():
#     # Check if user is logged in
#     if st.session_state.user_id is None:
#         if st.session_state.current_page == "login":
#             show_login_page()
#         elif st.session_state.current_page == "register":
#             show_register_page()
#         else:
#             st.session_state.current_page = "login"
#             st.rerun()
#     else:
#         show_dashboard()


def main():
    # Initialize database
    from models import init_database
    init_database()
    
    # Check if user is logged in
    if st.session_state.user_id is None:
        if st.session_state.current_page == "login":
            show_login_page()
        elif st.session_state.current_page == "register":
            show_register_page()
        else:
            st.session_state.current_page = "login"
            st.rerun()
    else:
        show_dashboard()
if __name__ == "__main__":
    main()