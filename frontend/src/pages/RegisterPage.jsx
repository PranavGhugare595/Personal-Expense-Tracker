import { useState } from 'react';
import { Link } from 'react-router-dom';
import { User, Lock, Eye, EyeOff, ShieldCheck, AlertCircle, CheckCircle, Inbox } from 'lucide-react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    password: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const [registered, setRegistered] = useState(false);
  const [resending, setResending] = useState(false);
  const [resendMsg, setResendMsg] = useState('');

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    if (error) setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!formData.full_name || !formData.email || !formData.password) {
      setError('Please fill in all required fields.');
      return;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters.');
      return;
    }

    setLoading(true);
    try {
      await axios.post(`${API_URL}/api/v1/auth/register`, {
        full_name: formData.full_name,
        email: formData.email,
        password: formData.password,
      });
      setSuccess('Account created! Please check your email to verify your account.');
      setRegistered(true);
    } catch (err) {
      console.error('Register error:', err);
      setError(
        err.response?.data?.detail || err.response?.data?.message || err.message || 'Registration failed. Please try again.'
      );
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
      setResendMsg(res.data.message || 'Verification email resent!');
    } catch {
      setResendMsg('Failed to resend. Please try again.');
    } finally {
      setResending(false);
    }
  };

  // ── Show "check your email" screen after successful registration ──
  if (registered) {
    return (
      <div className="auth-container">
        <div className="auth-card">
          <div className="auth-header">
            <div className="auth-logo" style={{ background: 'linear-gradient(135deg, rgba(16,185,129,0.12), rgba(52,211,153,0.12))' }}>
              <Inbox color="#10b981" />
            </div>
            <h1 className="auth-title" style={{ background: 'linear-gradient(135deg, #10b981, #34d399)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              Check Your Email
            </h1>
            <p className="auth-subtitle">
              We've sent a verification link to <strong>{formData.email}</strong>. Click the link in the email to activate your account.
            </p>
          </div>

          <div style={{ textAlign: 'center', marginTop: '0.5rem' }}>
            <button
              className="auth-button"
              onClick={handleResend}
              disabled={resending}
              id="resend-verify-btn"
              style={{ marginBottom: '0.75rem' }}
            >
              {resending ? 'Sending...' : 'Resend Verification Email'}
            </button>
            {resendMsg && (
              <p style={{ color: '#6b7280', fontSize: '0.85rem' }}>{resendMsg}</p>
            )}
          </div>

          <div className="auth-footer">
            Already verified?{' '}
            <Link to="/login" className="auth-link">Login Here</Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        {/* Header */}
        <div className="auth-header">
          <div className="auth-logo">
            <ShieldCheck />
          </div>
          <h1 className="auth-title">AI Expense Tracker</h1>
          <p className="auth-subtitle">Setup a new ML analytical account</p>
        </div>

        {/* Error */}
        {error && (
          <div className="error-message">
            <AlertCircle size={16} />
            {error}
          </div>
        )}

        {/* Success */}
        {success && (
          <div className="success-message">
            <CheckCircle size={16} />
            {success}
          </div>
        )}

        {/* Form */}
        <form className="auth-form" onSubmit={handleSubmit} id="register-form">
          {/* Full Name */}
          <div className="form-group">
            <label className="form-label" htmlFor="register-name">
              <span className="required">*</span> Full Name
            </label>
            <div className="input-wrapper">
              <span className="input-icon">
                <User />
              </span>
              <input
                id="register-name"
                type="text"
                name="full_name"
                className="form-input"
                placeholder="Enter your full name"
                value={formData.full_name}
                onChange={handleChange}
                autoComplete="name"
                required
              />
            </div>
          </div>

          {/* Email */}
          <div className="form-group">
            <label className="form-label" htmlFor="register-email">
              <span className="required">*</span> Email Address
            </label>
            <div className="input-wrapper">
              <span className="input-icon">
                <User />
              </span>
              <input
                id="register-email"
                type="email"
                name="email"
                className="form-input"
                placeholder="your.email@example.com"
                value={formData.email}
                onChange={handleChange}
                autoComplete="email"
                required
              />
            </div>
          </div>

          {/* Password */}
          <div className="form-group">
            <label className="form-label" htmlFor="register-password">
              <span className="required">*</span> Secret Password
            </label>
            <div className="input-wrapper">
              <span className="input-icon">
                <Lock />
              </span>
              <input
                id="register-password"
                type={showPassword ? 'text' : 'password'}
                name="password"
                className="form-input has-toggle"
                placeholder="Min 6 characters"
                value={formData.password}
                onChange={handleChange}
                autoComplete="new-password"
                required
                minLength={6}
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword(!showPassword)}
                aria-label={showPassword ? 'Hide password' : 'Show password'}
                id="register-password-toggle"
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
            id="register-submit-btn"
          >
            {loading && <span className="spinner" />}
            {loading ? 'Creating Account...' : 'Register Account'}
          </button>
        </form>

        {/* Footer */}
        <div className="auth-footer">
          Already have an account?{' '}
          <Link to="/login" className="auth-link">
            Login Here
          </Link>
        </div>
      </div>
    </div>
  );
}
