import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { supabase } from '../lib/supabase';
import {
  Activity,
  TrendingUp,
  Calendar,
  Stethoscope,
  MessageCircle,
  Flame,
} from 'lucide-react';

export default function Dashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    currentStreak: 0,
    longestStreak: 0,
    totalLogs: 0,
    recentLogs: [],
    recentTriage: [],
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, [user]);

  const fetchDashboardData = async () => {
    if (!user) return;

    const today = new Date().toISOString().split('T')[0];
    const sevenDaysAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
      .toISOString()
      .split('T')[0];

    const [logsResult, triageResult, streaksResult] = await Promise.all([
      supabase
        .from('health_logs')
        .select('*')
        .eq('user_id', user.id)
        .gte('date', sevenDaysAgo)
        .order('date', { ascending: false })
        .limit(5),
      supabase
        .from('triage_results')
        .select('*')
        .eq('user_id', user.id)
        .order('created_at', { ascending: false })
        .limit(3),
      supabase
        .from('daily_streaks')
        .select('*')
        .eq('user_id', user.id)
        .eq('completed', true)
        .order('date', { ascending: false }),
    ]);

    const streaks = streaksResult.data || [];
    let currentStreak = 0;
    const todayDate = new Date();

    for (let i = 0; i < streaks.length; i++) {
      const expectedDate = new Date(todayDate);
      expectedDate.setDate(expectedDate.getDate() - i);
      const expectedDateStr = expectedDate.toISOString().split('T')[0];

      if (streaks[i]?.date === expectedDateStr) {
        currentStreak++;
      } else {
        break;
      }
    }

    let longestStreak = 0;
    let tempStreak = 0;
    let prevDate = null;

    for (const streak of streaks.sort((a, b) =>
      a.date.localeCompare(b.date)
    )) {
      const currentDate = new Date(streak.date);
      if (prevDate) {
        const dayDiff = Math.floor(
          (currentDate - prevDate) / (1000 * 60 * 60 * 24)
        );
        if (dayDiff === 1) {
          tempStreak++;
        } else {
          tempStreak = 1;
        }
      } else {
        tempStreak = 1;
      }
      longestStreak = Math.max(longestStreak, tempStreak);
      prevDate = currentDate;
    }

    setStats({
      currentStreak,
      longestStreak: longestStreak || currentStreak,
      totalLogs: logsResult.data?.length || 0,
      recentLogs: logsResult.data || [],
      recentTriage: triageResult.data || [],
    });

    setLoading(false);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto fade-in">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Health Dashboard
        </h1>
        <p className="text-gray-600">
          Welcome back! Here's an overview of your health journey.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="card hover:scale-105">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-orange-100 rounded-lg">
              <Flame className="w-6 h-6 text-orange-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600 font-medium">
                Current Streak
              </p>
              <p className="text-2xl font-bold text-gray-900">
                {stats.currentStreak} days
              </p>
            </div>
          </div>
        </div>

        <div className="card hover:scale-105">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-blue-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600 font-medium">
                Longest Streak
              </p>
              <p className="text-2xl font-bold text-gray-900">
                {stats.longestStreak} days
              </p>
            </div>
          </div>
        </div>

        <div className="card hover:scale-105">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-green-100 rounded-lg">
              <Activity className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600 font-medium">Total Logs</p>
              <p className="text-2xl font-bold text-gray-900">
                {stats.totalLogs}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Recent Health Logs
          </h2>
          {stats.recentLogs.length > 0 ? (
            <div className="space-y-4">
              {stats.recentLogs.slice(0, 3).map((log) => (
                <div
                  key={log.id}
                  className="p-4 bg-gray-50 rounded-lg border border-gray-200"
                >
                  <div className="flex items-start justify-between mb-2">
                    <p className="text-sm font-medium text-gray-900">
                      {log.date}
                    </p>
                    {log.severity_score && (
                      <span className="badge badge-info">
                        Score: {log.severity_score}
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-600">
                    {log.symptoms.substring(0, 100)}
                    {log.symptoms.length > 100 ? '...' : ''}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              No health logs yet. Complete your daily check-in to get started!
            </div>
          )}
        </div>

        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Recent Triage Assessments
          </h2>
          {stats.recentTriage.length > 0 ? (
            <div className="space-y-4">
              {stats.recentTriage.map((triage) => (
                <div
                  key={triage.id}
                  className="p-4 bg-gray-50 rounded-lg border border-gray-200"
                >
                  <div className="flex items-start justify-between mb-2">
                    <p className="text-sm font-medium text-gray-900">
                      {new Date(triage.created_at).toLocaleDateString()}
                    </p>
                    <span
                      className={`badge ${
                        triage.triage_level === 'self-monitor'
                          ? 'badge-success'
                          : 'badge-warning'
                      }`}
                    >
                      {triage.triage_level === 'self-monitor'
                        ? 'Self Monitor'
                        : 'Visit Doctor'}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">
                    {triage.symptoms.substring(0, 80)}
                    {triage.symptoms.length > 80 ? '...' : ''}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              No triage assessments yet. Use the Symptom Triage tool!
            </div>
          )}
        </div>
      </div>

      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => navigate('/daily-checkin')}
            className="btn btn-primary flex items-center justify-center gap-2 py-4"
          >
            <Calendar className="w-5 h-5" />
            Daily Check-in
          </button>
          <button
            onClick={() => navigate('/triage')}
            className="btn btn-outline flex items-center justify-center gap-2 py-4"
          >
            <Stethoscope className="w-5 h-5" />
            Symptom Triage
          </button>
          <button
            onClick={() => navigate('/assistant')}
            className="btn btn-outline flex items-center justify-center gap-2 py-4"
          >
            <MessageCircle className="w-5 h-5" />
            Health Assistant
          </button>
        </div>
      </div>
    </div>
  );
}
