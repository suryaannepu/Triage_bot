import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { supabase } from '../lib/supabase';
import { CheckCircle, AlertCircle } from 'lucide-react';

export default function DailyCheckin() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [symptoms, setSymptoms] = useState('');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [alreadyCompleted, setAlreadyCompleted] = useState(false);
  const [todayLog, setTodayLog] = useState(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    checkTodayLog();
  }, [user]);

  const checkTodayLog = async () => {
    if (!user) return;

    const today = new Date().toISOString().split('T')[0];

    const { data } = await supabase
      .from('health_logs')
      .select('*')
      .eq('user_id', user.id)
      .eq('date', today)
      .maybeSingle();

    if (data) {
      setAlreadyCompleted(true);
      setTodayLog(data);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const today = new Date().toISOString().split('T')[0];

      const severityScore = Math.floor(Math.random() * 30) + 20;

      const { error: logError } = await supabase.from('health_logs').insert({
        user_id: user.id,
        date: today,
        symptoms,
        notes,
        severity_score: severityScore,
      });

      if (logError) throw logError;

      const { error: streakError } = await supabase
        .from('daily_streaks')
        .insert({
          user_id: user.id,
          date: today,
          completed: true,
        });

      if (streakError && streakError.code !== '23505') throw streakError;

      setSuccess(true);
      setTimeout(() => {
        navigate('/dashboard');
      }, 2000);
    } catch (error) {
      console.error('Error saving check-in:', error);
      alert('Error saving check-in. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = async () => {
    if (!todayLog) return;

    const today = new Date().toISOString().split('T')[0];

    await supabase
      .from('health_logs')
      .delete()
      .eq('user_id', user.id)
      .eq('date', today);

    await supabase
      .from('daily_streaks')
      .delete()
      .eq('user_id', user.id)
      .eq('date', today);

    setAlreadyCompleted(false);
    setTodayLog(null);
  };

  if (success) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="card text-center py-12 fade-in">
          <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Check-in Completed!
          </h2>
          <p className="text-gray-600">
            Great job! Your daily health log has been saved.
          </p>
        </div>
      </div>
    );
  }

  if (alreadyCompleted && todayLog) {
    return (
      <div className="max-w-2xl mx-auto fade-in">
        <div className="card">
          <div className="flex items-center gap-3 mb-6">
            <CheckCircle className="w-8 h-8 text-green-600" />
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                Already Completed
              </h2>
              <p className="text-gray-600">
                You've completed your daily check-in for today
              </p>
            </div>
          </div>

          <div className="space-y-4 mb-6">
            <div>
              <label className="label">Symptoms</label>
              <div className="p-4 bg-gray-50 rounded-lg">
                {todayLog.symptoms}
              </div>
            </div>

            {todayLog.notes && (
              <div>
                <label className="label">Notes</label>
                <div className="p-4 bg-gray-50 rounded-lg">{todayLog.notes}</div>
              </div>
            )}

            {todayLog.severity_score && (
              <div>
                <label className="label">Severity Score</label>
                <div className="p-4 bg-gray-50 rounded-lg">
                  {todayLog.severity_score}/100
                </div>
              </div>
            )}
          </div>

          <button onClick={handleUpdate} className="btn btn-outline w-full">
            Update Today's Entry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto fade-in">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Daily Health Check-in
        </h1>
        <p className="text-gray-600">
          Record your daily health status and symptoms
        </p>
      </div>

      <div className="card">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="label">How are you feeling today?</label>
            <textarea
              className="textarea"
              placeholder="Describe any symptoms or concerns..."
              value={symptoms}
              onChange={(e) => setSymptoms(e.target.value)}
              required
              rows={5}
            />
          </div>

          <div>
            <label className="label">Additional Notes (optional)</label>
            <textarea
              className="textarea"
              placeholder="Any additional information about your health today..."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={3}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary w-full"
          >
            {loading ? 'Submitting...' : 'Submit Check-in'}
          </button>
        </form>
      </div>
    </div>
  );
}
