import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { supabase } from '../lib/supabase';
import { Stethoscope, AlertCircle, CheckCircle } from 'lucide-react';

export default function SymptomTriage() {
  const { user } = useAuth();
  const [symptoms, setSymptoms] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);

    try {
      const response = await fetch(
        `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/triage-assessment`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${import.meta.env.VITE_SUPABASE_ANON_KEY}`,
          },
          body: JSON.stringify({ symptoms }),
        }
      );

      const data = await response.json();

      await supabase.from('triage_results').insert({
        user_id: user.id,
        symptoms,
        triage_level: data.triage_level,
        confidence: data.confidence,
        reasoning: data.reasoning,
        recommended_action: data.recommended_action,
        detailed_analysis: data.detailed_analysis || '',
      });

      setResult(data);
    } catch (error) {
      console.error('Error:', error);
      alert('Error analyzing symptoms. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto fade-in">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-3">
          <Stethoscope className="w-8 h-8 text-blue-600" />
          Symptom Triage Assessment
        </h1>
        <div className="alert alert-info">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>
            This tool provides AI-powered triage recommendations but is not a
            substitute for professional medical advice.
          </span>
        </div>
      </div>

      <div className="card mb-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="label">Describe your symptoms in detail</label>
            <textarea
              className="textarea"
              placeholder="e.g., I've had a persistent headache for 3 days, accompanied by nausea..."
              value={symptoms}
              onChange={(e) => setSymptoms(e.target.value)}
              required
              rows={6}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary w-full"
          >
            {loading ? 'Analyzing...' : 'Analyze Symptoms'}
          </button>
        </form>
      </div>

      {result && (
        <div className="card fade-in">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Assessment Results
          </h2>

          <div
            className={`p-6 rounded-lg mb-6 ${
              result.triage_level === 'self-monitor'
                ? 'bg-green-50 border-2 border-green-200'
                : 'bg-yellow-50 border-2 border-yellow-200'
            }`}
          >
            <div className="flex items-start gap-4 mb-4">
              {result.triage_level === 'self-monitor' ? (
                <CheckCircle className="w-8 h-8 text-green-600 flex-shrink-0" />
              ) : (
                <AlertCircle className="w-8 h-8 text-yellow-600 flex-shrink-0" />
              )}
              <div>
                <h3 className="text-xl font-bold mb-1">
                  {result.triage_level === 'self-monitor'
                    ? 'Self Monitor'
                    : 'Visit Doctor'}
                </h3>
                <span className="badge badge-info">
                  {result.confidence} Confidence
                </span>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <h4 className="font-semibold text-gray-900 mb-1">Reasoning</h4>
                <p className="text-gray-700">{result.reasoning}</p>
              </div>

              <div>
                <h4 className="font-semibold text-gray-900 mb-1">
                  Recommended Action
                </h4>
                <p className="text-gray-700">{result.recommended_action}</p>
              </div>

              {result.detailed_analysis && (
                <div>
                  <h4 className="font-semibold text-gray-900 mb-1">
                    Detailed Analysis
                  </h4>
                  <p className="text-gray-700">{result.detailed_analysis}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
