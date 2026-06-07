import { useState, useEffect } from 'react';
import { User, Shield, CreditCard } from 'lucide-react';
import api from '../utils/api';
import { currencies } from '../utils/currencies';
import './ProfilePage.css';

export default function ProfilePage() {
  const [profile, setProfile] = useState({
    full_name: '',
    email: '',
    currency: 'INR',
    monthly_income: 0,
    savings_target: 20
  });
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });
  
  const [loading, setLoading] = useState(true);
  const [savingProfile, setSavingProfile] = useState(false);
  const [savingPassword, setSavingPassword] = useState(false);
  const [profileMsg, setProfileMsg] = useState({ type: '', text: '' });
  const [passMsg, setPassMsg] = useState({ type: '', text: '' });

  useEffect(() => {
    api.get('/api/v1/profile')
      .then(res => {
        setProfile(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load profile', err);
        setLoading(false);
      });
  }, []);

  const handleProfileChange = (e) => {
    setProfile({ ...profile, [e.target.name]: e.target.value });
    setProfileMsg({ type: '', text: '' });
  };

  const handlePasswordChange = (e) => {
    setPasswordData({ ...passwordData, [e.target.name]: e.target.value });
    setPassMsg({ type: '', text: '' });
  };

  const submitProfile = async (e) => {
    e.preventDefault();
    setSavingProfile(true);

    const payload = {};
    if (profile.full_name?.trim()) payload.full_name = profile.full_name.trim();
    if (profile.currency) payload.currency = profile.currency;

    const incomeValue = parseFloat(profile.monthly_income);
    if (!Number.isNaN(incomeValue)) payload.monthly_income = incomeValue;

    const savingsValue = parseInt(profile.savings_target, 10);
    if (!Number.isNaN(savingsValue)) payload.savings_target = savingsValue;

    try {
      const res = await api.put('/api/v1/profile', payload);
      setProfile(res.data);
      localStorage.setItem('user', JSON.stringify(res.data));
      window.dispatchEvent(new Event('userUpdated'));
      setProfileMsg({ type: 'success', text: 'Profile updated successfully!' });
    } catch (err) {
      setProfileMsg({ type: 'error', text: err.response?.data?.detail || 'Failed to update profile.' });
    } finally {
      setSavingProfile(false);
    }
  };

  const submitPassword = async (e) => {
    e.preventDefault();
    setSavingPassword(true);
    try {
      await api.put('/api/v1/profile/password', passwordData);
      setPassMsg({ type: 'success', text: 'Password changed successfully!' });
      setPasswordData({ current_password: '', new_password: '', confirm_password: '' });
    } catch (err) {
      setPassMsg({ type: 'error', text: err.response?.data?.detail || 'Failed to change password.' });
    } finally {
      setSavingPassword(false);
    }
  };

  if (loading) return <div style={{ padding: '2rem' }}>Loading profile...</div>;

  return (
    <div className="profile-container" style={{ maxWidth: '800px', margin: '0 auto' }}>
      <div className="profile-card" style={{ background: 'white', padding: '2rem', borderRadius: '12px', border: '1px solid #e5e7eb', marginBottom: '2rem' }}>
        <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem', fontSize: '1.25rem' }}>
          <User size={20} /> Personal Information
        </h2>
        
        {profileMsg.text && (
          <div style={{ color: profileMsg.type === 'success' ? 'green' : 'red', marginBottom: '1rem' }}>
            {profileMsg.text}
          </div>
        )}

        <form onSubmit={submitProfile} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.85rem' }}>Full Name</label>
            <input type="text" name="full_name" value={profile.full_name || ''} onChange={handleProfileChange} style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #d1d5db' }} required />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.85rem' }}>Email Address (Read Only)</label>
            <input type="email" value={profile.email || ''} readOnly style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #d1d5db', background: '#f3f4f6', color: '#6b7280' }} />
          </div>
          
          <h3 style={{ marginTop: '1rem', fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <CreditCard size={18} /> Financial Settings
          </h3>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.85rem' }}>Base Currency</label>
              <select name="currency" value={profile.currency} onChange={handleProfileChange} style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #d1d5db' }}>
                {currencies.map(c => <option key={c.code} value={c.code}>{c.code} - {c.name}</option>)}
              </select>
            </div>
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.85rem' }}>Monthly Income</label>
              <input type="number" name="monthly_income" value={profile.monthly_income} onChange={handleProfileChange} style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #d1d5db' }} />
            </div>
          </div>
          
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.85rem' }}>Savings Target (% of income)</label>
            <input type="number" name="savings_target" min="0" max="100" value={profile.savings_target} onChange={handleProfileChange} style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #d1d5db' }} />
          </div>
          
          <button type="submit" disabled={savingProfile} style={{ padding: '0.75rem', background: '#10b981', color: 'white', borderRadius: '8px', border: 'none', cursor: 'pointer', marginTop: '1rem' }}>
            {savingProfile ? 'Saving...' : 'Save Profile Settings'}
          </button>
        </form>
      </div>

      <div className="profile-card" style={{ background: 'white', padding: '2rem', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
        <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem', fontSize: '1.25rem' }}>
          <Shield size={20} /> Security Settings
        </h2>
        
        {passMsg.text && (
          <div style={{ color: passMsg.type === 'success' ? 'green' : 'red', marginBottom: '1rem' }}>
            {passMsg.text}
          </div>
        )}

        <form onSubmit={submitPassword} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.85rem' }}>Current Password</label>
            <input type="password" name="current_password" value={passwordData.current_password} onChange={handlePasswordChange} style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #d1d5db' }} required />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.85rem' }}>New Password</label>
              <input type="password" name="new_password" value={passwordData.new_password} onChange={handlePasswordChange} style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #d1d5db' }} required minLength="6" />
            </div>
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.85rem' }}>Confirm New Password</label>
              <input type="password" name="confirm_password" value={passwordData.confirm_password} onChange={handlePasswordChange} style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #d1d5db' }} required />
            </div>
          </div>
          <button type="submit" disabled={savingPassword} style={{ padding: '0.75rem', background: '#3b82f6', color: 'white', borderRadius: '8px', border: 'none', cursor: 'pointer', marginTop: '1rem' }}>
            {savingPassword ? 'Updating...' : 'Update Password'}
          </button>
        </form>
      </div>
    </div>
  );
}
