import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from '../api';
import { useToast } from '../context/ToastContext';

const EMPTY = {
  name: '',
  email: '',
  portal_username: '',
  portal_password: '',
  app_password: '',
  app_password_confirm: '',
};

export default function Register() {
  const navigate  = useNavigate();
  const showToast = useToast();

  const [form, setForm]       = useState(EMPTY);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState('');

  const handleChange = (e) => {
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }));
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (form.app_password !== form.app_password_confirm) {
      setError('Passwords do not match');
      return;
    }
    if (form.app_password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    setLoading(true);
    try {
      await api.register({
        name:            form.name,
        email:           form.email,
        portal_username: form.portal_username,
        portal_password: form.portal_password,
        app_password:    form.app_password,
      });
      showToast('Account created! Please sign in.', 'success');
      navigate('/login', { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-split">

      {/* ── Left panel ── */}
      <div className="login-left">
        <div className="login-left-inner">

          {/* Branding */}
          <div className="login-brand">
            <img src="/msritlogo.png" alt="MSRIT" className="login-brand-logo-img" />
            <div>
              <div className="login-brand-name">MSRIT</div>
              <div className="login-brand-dept">M S Ramaiah Institute of Technology</div>
            </div>
          </div>

          {/* Welcome */}
          <div className="login-welcome">
            <h1 className="login-welcome-heading">Faculty Account<br />Registration</h1>
            <p className="login-welcome-desc">
              Register your faculty account to access the attendance management portal.
              You will need your staff portal credentials to complete registration.
            </p>
          </div>

          {/* Steps */}
          <div className="login-info-grid">
            <div className="login-info-card">
              <div className="login-info-accent" />
              <div>
                <div className="login-info-label">Step 1 — Identity</div>
                <div className="login-info-value">Provide your full name and official MSRIT email address</div>
              </div>
            </div>
            <div className="login-info-card">
              <div className="login-info-accent" />
              <div>
                <div className="login-info-label">Step 2 — Portal Credentials</div>
                <div className="login-info-value">Enter your existing staff portal username and password for scraper access</div>
              </div>
            </div>
            <div className="login-info-card">
              <div className="login-info-accent" />
              <div>
                <div className="login-info-label">Step 3 — Set Password</div>
                <div className="login-info-value">Create a separate password to log in to this attendance portal</div>
              </div>
            </div>
          </div>

          {/* Notice */}
          <div className="login-notice">
            <div className="login-notice-header">
              <span className="login-notice-dot" />
              Important
            </div>
            <p className="login-notice-text">
              Your portal credentials are stored encrypted and used only to
              fetch attendance data on your behalf. Contact your administrator
              if you do not have staff portal access.
            </p>
          </div>

          {/* Footer */}
          <div className="login-left-footer">
            Autonomous Institution — Affiliated to Visvesvaraya Technological University
          </div>

        </div>
      </div>

      {/* ── Right panel — registration form ── */}
      <div className="login-right">
        <div className="login-form-card register-form-card">

          <div className="login-form-header">
            <div className="login-form-logo">
              <img src="/msritlogo.png" alt="MSRIT" className="login-form-logo-img" />
              <div>
                <div className="login-form-logo-title">MSRIT</div>
                <div className="login-form-logo-sub">Attendance Portal</div>
              </div>
            </div>
            <h2 className="login-form-heading">Create Account</h2>
            <p className="login-form-subheading">Faculty registration — all fields required</p>
          </div>

          {error && <div className="login-form-error">{error}</div>}

          <form onSubmit={handleSubmit} className="login-form-body">

            {/* Identity */}
            <div className="login-field">
              <label className="login-label" htmlFor="name">Full Name</label>
              <input
                id="name"
                name="name"
                type="text"
                className="login-input"
                placeholder="Dr. Jane Smith"
                value={form.name}
                onChange={handleChange}
                required
                autoFocus
              />
            </div>

            <div className="login-field">
              <label className="login-label" htmlFor="email">Email Address</label>
              <input
                id="email"
                name="email"
                type="email"
                className="login-input"
                placeholder="you@msrit.edu"
                value={form.email}
                onChange={handleChange}
                required
              />
            </div>

            {/* Portal credentials */}
            <div className="register-section-divider">Portal Credentials</div>

            <div className="login-field">
              <label className="login-label" htmlFor="portal_username">Portal Username</label>
              <input
                id="portal_username"
                name="portal_username"
                type="text"
                className="login-input"
                placeholder="Staff portal login username"
                value={form.portal_username}
                onChange={handleChange}
                required
              />
            </div>

            <div className="login-field">
              <label className="login-label" htmlFor="portal_password">Portal Password</label>
              <input
                id="portal_password"
                name="portal_password"
                type="password"
                className="login-input"
                placeholder="Staff portal login password"
                value={form.portal_password}
                onChange={handleChange}
                required
              />
            </div>

            {/* App password */}
            <div className="register-section-divider">Portal Login Password</div>

            <div className="login-field">
              <label className="login-label" htmlFor="app_password">Password</label>
              <input
                id="app_password"
                name="app_password"
                type="password"
                className="login-input"
                placeholder="Min. 6 characters"
                value={form.app_password}
                onChange={handleChange}
                required
                minLength={6}
              />
            </div>

            <div className="login-field">
              <label className="login-label" htmlFor="app_password_confirm">Confirm Password</label>
              <input
                id="app_password_confirm"
                name="app_password_confirm"
                type="password"
                className="login-input"
                placeholder="Repeat your password"
                value={form.app_password_confirm}
                onChange={handleChange}
                required
              />
            </div>

            <button
              type="submit"
              className="login-btn"
              disabled={loading}
            >
              {loading
                ? <><span className="login-spinner" /> Creating account…</>
                : 'Create Account'}
            </button>

          </form>

          <p className="login-form-footer">
            Already have an account?{' '}
            <Link to="/login" className="login-form-link">Sign in</Link>
          </p>

        </div>
      </div>

    </div>
  );
}
