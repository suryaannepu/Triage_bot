# Health Tracker

A modern web application for tracking personal health metrics, managing symptoms, and getting AI-powered health insights.

## Features

- **User Authentication**: Secure email/password authentication with Supabase
- **Daily Health Check-ins**: Log daily symptoms and health status with severity scoring
- **Symptom Triage**: AI-powered symptom assessment using Google Gemini
- **Health Assistant**: Interactive chat interface for health-related questions
- **Health Trends**: Visual analytics and charts showing health patterns over time
- **Medical Reports**: Export health data in CSV or JSON format
- **User Profile**: Comprehensive medical profile management

## Tech Stack

### Frontend
- React 19 with Vite
- React Router for navigation
- Supabase Client for authentication and database
- Recharts for data visualization
- Lucide React for icons
- Modern CSS with custom design system

### Backend
- Supabase (PostgreSQL database)
- Row Level Security (RLS) for data protection
- Supabase Edge Functions for AI integration
- Google Gemini API for health assessments

## Getting Started

### Prerequisites
- Node.js 18+ installed
- Supabase account
- Google Gemini API key (optional, for AI features)

### Installation

1. Clone the repository and install dependencies:
```bash
cd frontend
npm install
```

2. Configure environment variables:
Create a `.env` file in the `frontend` directory with:
```
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_AI_API_KEY=your_gemini_api_key
```

3. Start the development server:
```bash
npm run dev
```

Or from the project root:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

### Building for Production

```bash
npm run build
```

## Database Schema

The application uses the following main tables:

- **users**: User accounts and profile information
- **health_logs**: Daily health check-in entries
- **triage_results**: AI symptom triage assessments
- **chat_sessions**: Health assistant conversations
- **chat_messages**: Individual chat messages
- **daily_streaks**: Tracking of daily check-in streaks

All tables use Row Level Security to ensure users can only access their own data.

## Features Overview

### Dashboard
- Current streak counter
- Recent health logs
- Recent triage assessments
- Quick action buttons

### Daily Check-in
- Record daily symptoms
- Add optional notes
- Automatic severity scoring
- Streak tracking

### Symptom Triage
- Detailed symptom description
- AI-powered triage assessment
- Confidence level indication
- Recommended actions

### Health Assistant
- Interactive chat interface
- Context-aware responses
- Health advice and information
- Message history

### Health Trends
- Time-range filtering (7 days to 1 year)
- Severity score line chart
- Triage level distribution pie chart
- Raw data table view

### Medical Reports
- Export data as CSV or JSON
- Comprehensive health history
- Shareable with healthcare providers

### Profile Management
- Personal information
- Medical history
- Allergies and medications
- Emergency contact information

## Security Features

- Supabase authentication with email/password
- Row Level Security (RLS) on all database tables
- Secure API endpoints
- User data isolation
- Password hashing

## Design Philosophy

The application follows a clean, professional design with:
- Blue and green color scheme for trust and health
- Clear typography hierarchy
- Smooth animations and transitions
- Responsive design for all screen sizes
- Intuitive navigation
- Accessibility considerations

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## License

This project is private and proprietary.

## Notes

- The AI features require a Gemini API key and Supabase Edge Functions
- Database migrations should be applied before first use
- The application is designed for personal health tracking and should not replace professional medical advice
