import { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { supabase } from '../lib/supabase';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

export default function HealthTrends() {
  const { user } = useAuth();
  const [healthLogs, setHealthLogs] = useState([]);
  const [triageData, setTriageData] = useState([]);
  const [timeRange, setTimeRange] = useState('30');

  useEffect(() => {
    fetchData();
  }, [user, timeRange]);

  const fetchData = async () => {
    if (!user) return;

    const daysAgo = new Date();
    daysAgo.setDate(daysAgo.getDate() - parseInt(timeRange));
    const cutoffDate = daysAgo.toISOString().split('T')[0];

    const [logsResult, triageResult] = await Promise.all([
      supabase
        .from('health_logs')
        .select('*')
        .eq('user_id', user.id)
        .gte('date', cutoffDate)
        .order('date', { ascending: true }),
      supabase
        .from('triage_results')
        .select('*')
        .eq('user_id', user.id)
        .gte('created_at', cutoffDate + 'T00:00:00')
        .order('created_at', { ascending: false }),
    ]);

    setHealthLogs(logsResult.data || []);
    setTriageData(triageResult.data || []);
  };

  const triageDistribution = triageData.reduce((acc, item) => {
    acc[item.triage_level] = (acc[item.triage_level] || 0) + 1;
    return acc;
  }, {});

  const pieData = Object.entries(triageDistribution).map(([name, value]) => ({
    name: name === 'self-monitor' ? 'Self Monitor' : 'Visit Doctor',
    value,
  }));

  const COLORS = ['#10b981', '#f59e0b'];

  return (
    <div className="max-w-7xl mx-auto fade-in">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Health Trends & Analytics
        </h1>
        <p className="text-gray-600">
          Visualize your health data over time
        </p>
      </div>

      <div className="mb-6">
        <select
          className="input max-w-xs"
          value={timeRange}
          onChange={(e) => setTimeRange(e.target.value)}
        >
          <option value="7">Last 7 days</option>
          <option value="30">Last 30 days</option>
          <option value="90">Last 90 days</option>
          <option value="365">Last year</option>
        </select>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Health Severity Trends
          </h2>
          {healthLogs.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={healthLogs}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                />
                <YAxis />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="severity_score"
                  stroke="#2563eb"
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-center py-12 text-gray-500">
              No data available for the selected time range
            </div>
          )}
        </div>

        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Triage Level Distribution
          </h2>
          {pieData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) =>
                    `${name}: ${(percent * 100).toFixed(0)}%`
                  }
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-center py-12 text-gray-500">
              No triage data available for the selected time range
            </div>
          )}
        </div>
      </div>

      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Recent Health Data
        </h2>
        {healthLogs.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-3 font-semibold">Date</th>
                  <th className="text-left p-3 font-semibold">Symptoms</th>
                  <th className="text-left p-3 font-semibold">Severity</th>
                </tr>
              </thead>
              <tbody>
                {healthLogs.slice(-10).reverse().map((log) => (
                  <tr key={log.id} className="border-b hover:bg-gray-50">
                    <td className="p-3">{log.date}</td>
                    <td className="p-3">
                      {log.symptoms.substring(0, 60)}
                      {log.symptoms.length > 60 ? '...' : ''}
                    </td>
                    <td className="p-3">
                      <span className="badge badge-info">
                        {log.severity_score}/100
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            No health logs available yet
          </div>
        )}
      </div>
    </div>
  );
}
