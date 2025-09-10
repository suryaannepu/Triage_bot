import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

def create_health_trends_chart(health_logs: list) -> go.Figure:
    """Create health trends visualization"""
    if not health_logs:
        return create_empty_chart("No health data available")
    
    # Prepare data
    df = pd.DataFrame(health_logs)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # Create figure
    fig = make_subplots(specs=[[{"secondary_y": False}]])
    
    # Add severity score line
    fig.add_trace(
        go.Scatter(
            x=df['date'], 
            y=df['severity_score'],
            mode='lines+markers',
            name='Severity Score',
            line=dict(color='#1f77b4'),
            hovertemplate='<b>Date:</b> %{x}<br><b>Score:</b> %{y}<extra></extra>'
        )
    )
    
    # Update layout
    fig.update_layout(
        title='Health Trends Over Time',
        xaxis_title='Date',
        yaxis_title='Severity Score (0-100)',
        hovermode='x unified',
        showlegend=True,
        height=400
    )
    
    return fig

def create_streak_visualization(streak_data: dict) -> go.Figure:
    """Create visualization for streak data"""
    # Create a simple metric display
    fig = go.Figure()
    
    fig.add_trace(go.Indicator(
        mode="number",
        value=streak_data['current_streak'],
        title={"text": "Current Streak<br><span style='font-size:0.8em;color:gray'>Days</span>"},
        number={'font': {'size': 50}},
        domain={'x': [0, 0.3], 'y': [0, 1]}
    ))
    
    fig.add_trace(go.Indicator(
        mode="number",
        value=streak_data['longest_streak'],
        title={"text": "Longest Streak<br><span style='font-size:0.8em;color:gray'>Days</span>"},
        number={'font': {'size': 50}},
        domain={'x': [0.35, 0.65], 'y': [0, 1]}
    ))
    
    fig.add_trace(go.Indicator(
        mode="number",
        value=streak_data['total_logs'],
        title={"text": "Total Logs<br><span style='font-size:0.8em;color:gray'>Entries</span>"},
        number={'font': {'size': 50}},
        domain={'x': [0.7, 1], 'y': [0, 1]}
    ))
    
    fig.update_layout(
        height=200,
        margin=dict(l=10, r=10, t=50, b=10)
    )
    
    return fig

def create_triage_distribution_chart(triage_history: list) -> go.Figure:
    """Create chart showing distribution of triage levels"""
    if not triage_history:
        return create_empty_chart("No triage data available")
    
    # Count triage levels
    triage_counts = {}
    for result in triage_history:
        level = result['triage_level']
        triage_counts[level] = triage_counts.get(level, 0) + 1
    
    # Create pie chart
    fig = go.Figure(data=[go.Pie(
        labels=list(triage_counts.keys()),
        values=list(triage_counts.values()),
        hole=.3
    )])
    
    fig.update_layout(
        title='Triage Level Distribution',
        height=300
    )
    
    return fig

def create_daily_patterns_chart(health_logs: list) -> go.Figure:
    """Create chart showing patterns by time of day"""
    if not health_logs:
        return create_empty_chart("No health data available")
    
    # Extract hour from timestamps
    df = pd.DataFrame(health_logs)
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['hour'] = df['created_at'].dt.hour
    
    # Group by hour and calculate average severity
    hourly_avg = df.groupby('hour')['severity_score'].mean().reset_index()
    
    # Create bar chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=hourly_avg['hour'],
        y=hourly_avg['severity_score'],
        name='Average Severity',
        marker_color='indianred'
    ))
    
    fig.update_layout(
        title='Average Severity by Hour of Day',
        xaxis_title='Hour of Day',
        yaxis_title='Average Severity Score',
        xaxis=dict(tickmode='linear', dtick=1),
        height=300
    )
    
    return fig

def create_empty_chart(message: str) -> go.Figure:
    """Create an empty chart with a message"""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=16)
    )
    fig.update_layout(
        height=300,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )
    return fig