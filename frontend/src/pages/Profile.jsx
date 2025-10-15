import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { supabase } from '../lib/supabase';
import { User, CheckCircle } from 'lucide-react';

export default function Profile() {
  const { user } = useAuth();
  const [profile, setProfile] = useState({
    full_name: '',
    date_of_birth: '',
    blood_group: '',
    height: '',
    weight: '',
    allergies: '',
    medications: '',
    chronic_conditions: '',
    emergency_contact: '',
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    fetchProfile();
  }, [user]);

  const fetchProfile = async () => {
    if (!user) return;

    const { data } = await supabase
      .from('users')
      .select('*')
      .eq('id', user.id)
      .single();

    if (data) {
      setProfile({
        full_name: data.full_name || '',
        date_of_birth: data.date_of_birth || '',
        blood_group: data.blood_group || '',
        height: data.height || '',
        weight: data.weight || '',
        allergies: data.allergies || '',
        medications: data.medications || '',
        chronic_conditions: data.chronic_conditions || '',
        emergency_contact: data.emergency_contact || '',
      });
    }
    setLoading(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setSuccess(false);

    try {
      const { error } = await supabase
        .from('users')
        .update(profile)
        .eq('id', user.id);

      if (error) throw error;

      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (error) {
      console.error('Error updating profile:', error);
      alert('Error updating profile');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto fade-in">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-3">
          <User className="w-8 h-8 text-blue-600" />
          User Profile
        </h1>
        <p className="text-gray-600">
          Manage your personal and medical information
        </p>
      </div>

      <div className="card">
        {success && (
          <div className="alert alert-success mb-6 flex items-center gap-2">
            <CheckCircle className="w-5 h-5" />
            Profile updated successfully!
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <h3 className="text-lg font-semibold mb-4">Personal Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">Email</label>
                <input
                  type="email"
                  className="input"
                  value={user.email}
                  disabled
                />
              </div>

              <div>
                <label className="label">Full Name</label>
                <input
                  type="text"
                  className="input"
                  value={profile.full_name}
                  onChange={(e) =>
                    setProfile({ ...profile, full_name: e.target.value })
                  }
                />
              </div>

              <div>
                <label className="label">Date of Birth</label>
                <input
                  type="date"
                  className="input"
                  value={profile.date_of_birth}
                  onChange={(e) =>
                    setProfile({ ...profile, date_of_birth: e.target.value })
                  }
                />
              </div>

              <div>
                <label className="label">Blood Group</label>
                <select
                  className="input"
                  value={profile.blood_group}
                  onChange={(e) =>
                    setProfile({ ...profile, blood_group: e.target.value })
                  }
                >
                  <option value="">Select</option>
                  <option value="A+">A+</option>
                  <option value="A-">A-</option>
                  <option value="B+">B+</option>
                  <option value="B-">B-</option>
                  <option value="AB+">AB+</option>
                  <option value="AB-">AB-</option>
                  <option value="O+">O+</option>
                  <option value="O-">O-</option>
                </select>
              </div>

              <div>
                <label className="label">Height (cm)</label>
                <input
                  type="number"
                  className="input"
                  value={profile.height}
                  onChange={(e) =>
                    setProfile({ ...profile, height: e.target.value })
                  }
                />
              </div>

              <div>
                <label className="label">Weight (kg)</label>
                <input
                  type="number"
                  className="input"
                  value={profile.weight}
                  onChange={(e) =>
                    setProfile({ ...profile, weight: e.target.value })
                  }
                />
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-4">Medical Information</h3>
            <div className="space-y-4">
              <div>
                <label className="label">Allergies</label>
                <textarea
                  className="textarea"
                  rows={2}
                  value={profile.allergies}
                  onChange={(e) =>
                    setProfile({ ...profile, allergies: e.target.value })
                  }
                />
              </div>

              <div>
                <label className="label">Current Medications</label>
                <textarea
                  className="textarea"
                  rows={2}
                  value={profile.medications}
                  onChange={(e) =>
                    setProfile({ ...profile, medications: e.target.value })
                  }
                />
              </div>

              <div>
                <label className="label">Chronic Conditions</label>
                <textarea
                  className="textarea"
                  rows={2}
                  value={profile.chronic_conditions}
                  onChange={(e) =>
                    setProfile({
                      ...profile,
                      chronic_conditions: e.target.value,
                    })
                  }
                />
              </div>

              <div>
                <label className="label">Emergency Contact Information</label>
                <textarea
                  className="textarea"
                  rows={2}
                  value={profile.emergency_contact}
                  onChange={(e) =>
                    setProfile({
                      ...profile,
                      emergency_contact: e.target.value,
                    })
                  }
                />
              </div>
            </div>
          </div>

          <button
            type="submit"
            disabled={saving}
            className="btn btn-primary w-full"
          >
            {saving ? 'Saving...' : 'Update Profile'}
          </button>
        </form>
      </div>
    </div>
  );
}
