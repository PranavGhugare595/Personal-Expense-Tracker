import { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { CheckCircle, XCircle, Mail, ArrowRight } from 'lucide-react';
import axios from 'axios';
import './VerifyEmailPage.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function VerifyEmailPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');

  const [status, setStatus] = useState('loading'); // loading | success | error
  const [message, setMessage] = useState('');
  const [countdown, setCountdown] = useState(5);
  const [resending, setResending] = useState(false);
  const [resendEmail, setResendEmail] = useState('');
  const [resendMsg, setResendMsg] = useState('');

  useEffect(() => {
    if (!token) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setStatus('error');
      setMessage('No verification token provided. Please check the link in your email.');
      return;
    }

    const verifyEmail = async () => {
      try {
        const res = await axios.get(`${API_URL}/api/v1/auth/verify-email`, {
          params: { token },
        });
        setStatus('success');
        setMessage(res.data.message || 'Email verified successfully!');
      } catch (err) {
        setStatus('error');
        setMessage(
          err.response?.data?.detail || 'Verification failed. The link may be expired or invalid.'
        );
      }
    };

    verifyEmail();
  }, [token]);

  // Countdown redirect on success
  useEffect(() => {
    if (status !== 'success') return;
    if (countdown <= 0) {
      window.location.href = '/login';
      return;
    }
    const timer = setTimeout(() => setCountdown((c) => c - 1), 1000);
    return () => clearTimeout(timer);
  }, [status, countdown]);

  const handleResend = async () => {
    if (!resendEmail) return;
    setResending(true);
    setResendMsg('');
    try {
      const res = await axios.post(`${API_URL}/api/v1/auth/resend-verification`, {
        email: resendEmail,
      });
      setResendMsg(res.data.message || 'Verification email sent!');
    } catch {
      setResendMsg('Failed to resend. Please try again.');
    } finally {
      setResending(false);
    }
  };

  return (
    <div className="verify-container">
      <div className="verify-card">
        {/* ── Loading ── */}
        {status === 'loading' && (
          <>
            <div className="verify-icon-wrapper loading">
              <div className="verify-spinner" />
            </div>
            <h1 className="verify-title loading">Verifying Your Email</h1>
            <p className="verify-subtitle">
              Please wait while we confirm your email address...
            </p>
          </>
        )}

        {/* ── Success ── */}
        {status === 'success' && (
          <>
            <div className="verify-icon-wrapper success">
              <CheckCircle size={38} color="#10b981" />
            </div>
            <h1 className="verify-title success">Email Verified!</h1>
            <p className="verify-subtitle">{message}</p>
            <div className="verify-actions">
              <Link to="/login" className="verify-btn primary" id="verify-goto-login">
                Go to Login <ArrowRight size={16} />
              </Link>
              <p className="verify-countdown">
                Redirecting in {countdown}s...
              </p>
            </div>
          </>
        )}

        {/* ── Error ── */}
        {status === 'error' && (
          <>
            <div className="verify-icon-wrapper error">
              <XCircle size={38} color="#ef4444" />
            </div>
            <h1 className="verify-title error">Verification Failed</h1>
            <p className="verify-subtitle">{message}</p>

            <div className="verify-actions">
              {/* Resend form */}
              <div style={{ width: '100%', marginBottom: '0.5rem' }}>
                <div className="input-wrapper" style={{ marginBottom: '0.75rem' }}>
                  <span className="input-icon"><Mail size={18} /></span>
                  <input
                    id="resend-email-input"
                    type="email"
                    className="form-input"
                    placeholder="Enter your email address"
                    value={resendEmail}
                    onChange={(e) => setResendEmail(e.target.value)}
                    style={{ paddingLeft: '2.8rem', fontSize: '0.88rem' }}
                  />
                </div>
                <button
                  className="verify-btn primary"
                  onClick={handleResend}
                  disabled={resending || !resendEmail}
                  id="resend-verify-btn"
                  style={{ width: '100%' }}
                >
                  <Mail size={16} />
                  {resending ? 'Sending...' : 'Resend Verification Email'}
                </button>
              </div>

              {resendMsg && (
                <p style={{ color: '#6b7280', fontSize: '0.85rem', marginTop: '0.5rem' }}>
                  {resendMsg}
                </p>
              )}

              <Link to="/login" className="verify-btn secondary" id="verify-back-login">
                Back to Login
              </Link>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
