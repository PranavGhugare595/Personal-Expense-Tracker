import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, Eye, EyeOff, ShieldCheck, AlertCircle, Inbox } from 'lucide-react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function LoginPage() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [needsVerification, setNeedsVerification] = useState(false);
  const [resending, setResending] = useState(false);
  const [resendMsg, setResendMsg] = useState('');

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    if (error) setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!formData.email || !formData.password) {
      setError('Please fill in all required fields.');
      return;
    }

    setLoading(true);
    setNeedsVerification(false);
    setResendMsg('');
    try {
      const res = await axios.post(`${API_URL}/api/v1/auth/login`, {
        email: formData.email,
        password: formData.password,
      });
      localStorage.setItem('token', res.data.access_token);
      localStorage.setItem('user', JSON.stringify(res.data.user));
      navigate('/dashboard');
    } catch (err) {
      console.error('Login error:', err);
      if (err.response?.status === 403) {
        setNeedsVerification(true);
        setError(err.response?.data?.detail || 'Please verify your email before logging in.');
      } else {
        setError(
          err.response?.data?.detail || err.response?.data?.message || err.message || 'Authentication failed. Please try again.'
        );
      }
    } finally {
      setLoading(false);
    }
  };

  const handleResend = async () => {
    setResending(true);
    setResendMsg('');
    try {
      const res = await axios.post(`${API_URL}/api/v1/auth/resend-verification`, {
        email: formData.email,
      });
      setResendMsg(res.data.message || 'Verification email sent!');
    } catch {
      setResendMsg('Failed to resend. Please try again.');
    } finally {
      setResending(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        {/* Header */}
        <div className="auth-header">
          <div className="auth-logo">
            <ShieldCheck />
          </div>
          <h1 className="auth-title">AI Expense Tracker</h1>
          <p className="auth-subtitle">Sign in to access your budget forecast</p>
        </div>

        {/* Error */}
        {error && (
          <div className="error-message">
            <AlertCircle size={16} />
            {error}
          </div>
        )}

        {/* Verification needed banner */}
        {needsVerification && (
          <div style={{ textAlign: 'center', marginBottom: '1rem' }}>
            <button
              className="auth-button"
              onClick={handleResend}
              disabled={resending || !formData.email}
              id="login-resend-verify-btn"
              style={{
                background: 'linear-gradient(135deg, #10b981, #34d399)',
                marginBottom: '0.5rem',
                fontSize: '0.85rem',
              }}
            >
              <Inbox size={16} style={{ marginRight: '0.4rem' }} />
              {resending ? 'Sending...' : 'Resend Verification Email'}
            </button>
            {resendMsg && (
              <p style={{ color: '#6b7280', fontSize: '0.82rem' }}>{resendMsg}</p>
            )}
          </div>
        )}

        {/* Form */}
        <form className="auth-form" onSubmit={handleSubmit} id="login-form">
          {/* Email */}
          <div className="form-group">
            <label className="form-label" htmlFor="login-email">
              <span className="required">*</span> Email Address
            </label>
            <div className="input-wrapper">
              <span className="input-icon">
                <Mail />
              </span>
              <input
                id="login-email"
                type="email"
                name="email"
                className="form-input"
                placeholder="A_ariel@example.com"
                value={formData.email}
                onChange={handleChange}
                autoComplete="email"
                required
              />
            </div>
          </div>

          {/* Password */}
          <div className="form-group">
            <label className="form-label" htmlFor="login-password">
              <span className="required">*</span> Secret Password
            </label>
            <div className="input-wrapper">
              <span className="input-icon">
                <Lock />
              </span>
              <input
                id="login-password"
                type={showPassword ? 'text' : 'password'}
                name="password"
                className="form-input has-toggle"
                placeholder="••••••••••"
                value={formData.password}
                onChange={handleChange}
                autoComplete="current-password"
                required
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword(!showPassword)}
                aria-label={showPassword ? 'Hide password' : 'Show password'}
                id="login-password-toggle"
              >
                {showPassword ? <EyeOff /> : <Eye />}
              </button>
            </div>
          </div>

          {/* Submit */}
          <button
            type="submit"
            className="auth-button"
            disabled={loading}
            id="login-submit-btn"
          >
            {loading && <span className="spinner" />}
            {loading ? 'Authenticating...' : 'Secure Authenticate'}
          </button>
        </form>

        {/* Footer */}
        <div className="auth-footer">
          Need a financial companion?{' '}
          <Link to="/register" className="auth-link">
            Sign Up Free
          </Link>
        </div>
      </div>
    </div>
  );
}
