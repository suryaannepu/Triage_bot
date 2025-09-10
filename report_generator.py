import pdfkit
from datetime import datetime
from database import get_health_logs, get_triage_history, get_user_profile
from gemini_client import generate_medical_report

def generate_pdf_report(user_id: int, start_date: str, end_date: str) -> str:
    """Generate a PDF medical report"""
    # Get data for the report
    user_profile = get_user_profile(user_id)
    health_logs = get_health_logs(user_id, 100)  # Get last 100 logs
    triage_history = get_triage_history(user_id, 20)  # Get last 20 triage results
    
    # Filter logs by date range
    if start_date and end_date:
        health_logs = [log for log in health_logs if start_date <= log['date'] <= end_date]
        triage_history = [triage for triage in triage_history if start_date <= triage['created_at'][:10] <= end_date]
    
    # Generate report content using AI
    report_content = generate_medical_report(user_profile, health_logs, triage_history)
    
    # Create HTML template for PDF
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Medical Health Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 40px; }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .section {{ margin-bottom: 20px; }}
            .section-title {{ 
                font-weight: bold; 
                font-size: 18px; 
                margin-bottom: 10px; 
                border-bottom: 2px solid #333; 
                padding-bottom: 5px; 
            }}
            .patient-info {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
            .summary-box {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Medical Health Report</h1>
            <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            <p>Period: {start_date} to {end_date}</p>
        </div>
        
        <div class="section">
            <div class="section-title">Patient Information</div>
            <div class="patient-info">
                <div><strong>Name:</strong> {user_profile.get('full_name', 'Not provided')}</div>
                <div><strong>Date of Birth:</strong> {user_profile.get('date_of_birth', 'Not provided')}</div>
                <div><strong>Blood Group:</strong> {user_profile.get('blood_group', 'Not provided')}</div>
                <div><strong>Height:</strong> {user_profile.get('height', 'Not provided')}</div>
                <div><strong>Weight:</strong> {user_profile.get('weight', 'Not provided')}</div>
                <div><strong>Allergies:</strong> {user_profile.get('allergies', 'None reported')}</div>
                <div><strong>Medications:</strong> {user_profile.get('medications', 'None reported')}</div>
                <div><strong>Chronic Conditions:</strong> {user_profile.get('chronic_conditions', 'None reported')}</div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">Report Summary</div>
            <div class="summary-box">
                {report_content.replace(chr(10), '<br>')}
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">Recent Health Logs ({len(health_logs)} entries)</div>
            <ul>
    """
    
    # Add health logs
    for log in health_logs[-10:]:  # Show last 10 logs
        html_template += f"""
                <li>
                    <strong>{log['date']}:</strong> {log['symptoms']} 
                    (Severity: {log.get('severity_score', 'N/A')}/100)
                </li>
        """
    
    html_template += """
            </ul>
        </div>
        
        <div class="section">
            <div class="section-title">Recent Triage Assessments</div>
            <ul>
    """
    
    # Add triage history
    for triage in triage_history[-5:]:  # Show last 5 triage results
        html_template += f"""
                <li>
                    <strong>{triage['created_at'][:10]}:</strong> {triage['symptoms']} 
                    -> {triage['triage_level']} ({triage['confidence']} confidence)
                </li>
        """
    
    html_template += """
            </ul>
        </div>
    </body>
    </html>
    """
    
    # Generate PDF from HTML
    try:
        # For this to work, you need to install wkhtmltopdf and add it to your PATH
        # Alternatively, you can use other PDF generation libraries
        pdf_data = pdfkit.from_string(html_template, False)
        return pdf_data
    except Exception as e:
        # Fallback: return HTML content
        print(f"PDF generation error: {e}")
        return html_template

def export_health_data(user_id: int, format_type: str = "csv") -> str:
    """Export health data in various formats"""
    health_logs = get_health_logs(user_id, 1000)  # Get up to 1000 logs
    triage_history = get_triage_history(user_id, 1000)  # Get up to 1000 triage results
    
    if format_type == "csv":
        # Create CSV content
        csv_content = "Type,Date,Content,Score,Additional Info\n"
        
        for log in health_logs:
            csv_content += f"Health Log,{log['date']},\"{log['symptoms']}\",{log.get('severity_score', '')},\"{log.get('notes', '')}\"\n"
        
        for triage in triage_history:
            csv_content += f"Triage,{triage['created_at']},\"{triage['symptoms']}\",,\"{triage['triage_level']} ({triage['confidence']})\"\n"
        
        return csv_content
    
    elif format_type == "json":
        # Create JSON content
        import json
        data = {
            "health_logs": health_logs,
            "triage_history": triage_history
        }
        return json.dumps(data, indent=2)
    
    else:
        return "Unsupported format"