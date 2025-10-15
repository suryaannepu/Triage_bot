import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { supabase } from '../lib/supabase';
import { FileText, Download } from 'lucide-react';

export default function MedicalReports() {
  const { user } = useAuth();
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [exportFormat, setExportFormat] = useState('csv');
  const [loading, setLoading] = useState(false);

  const handleExport = async () => {
    if (!user) return;
    setLoading(true);

    try {
      const { data: logs } = await supabase
        .from('health_logs')
        .select('*')
        .eq('user_id', user.id)
        .order('date', { ascending: false });

      const { data: triage } = await supabase
        .from('triage_results')
        .select('*')
        .eq('user_id', user.id)
        .order('created_at', { ascending: false });

      let content = '';
      let filename = `health_data_export.${exportFormat}`;
      let mimeType = 'text/csv';

      if (exportFormat === 'csv') {
        content = 'Type,Date,Content,Score,Additional Info\n';
        logs?.forEach((log) => {
          content += `Health Log,${log.date},"${log.symptoms.replace(/"/g, '""')}",${log.severity_score || ''},"${(log.notes || '').replace(/"/g, '""')}"\n`;
        });
        triage?.forEach((t) => {
          content += `Triage,${t.created_at.split('T')[0]},"${t.symptoms.replace(/"/g, '""')}",,"${t.triage_level} (${t.confidence})"\n`;
        });
      } else {
        mimeType = 'application/json';
        content = JSON.stringify(
          {
            health_logs: logs,
            triage_history: triage,
          },
          null,
          2
        );
      }

      const blob = new Blob([content], { type: mimeType });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Export error:', error);
      alert('Error exporting data');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto fade-in">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-3">
          <FileText className="w-8 h-8 text-blue-600" />
          Medical Reports & Export
        </h1>
        <p className="text-gray-600">
          Export your health data for sharing with healthcare providers
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Export Health Data
          </h2>

          <div className="space-y-4">
            <div>
              <label className="label">Export Format</label>
              <select
                className="input"
                value={exportFormat}
                onChange={(e) => setExportFormat(e.target.value)}
              >
                <option value="csv">CSV</option>
                <option value="json">JSON</option>
              </select>
            </div>

            <button
              onClick={handleExport}
              disabled={loading}
              className="btn btn-primary w-full flex items-center justify-center gap-2"
            >
              <Download className="w-5 h-5" />
              {loading ? 'Exporting...' : `Export as ${exportFormat.toUpperCase()}`}
            </button>
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            About Your Data
          </h2>
          <div className="space-y-3 text-sm text-gray-600">
            <p>
              Your exported data includes:
            </p>
            <ul className="list-disc list-inside space-y-2 ml-2">
              <li>All daily health logs</li>
              <li>Symptom triage assessments</li>
              <li>Health metrics and scores</li>
              <li>Timestamps for all entries</li>
            </ul>
            <p className="mt-4">
              This data can be shared with your healthcare provider to give
              them a comprehensive view of your health history.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
