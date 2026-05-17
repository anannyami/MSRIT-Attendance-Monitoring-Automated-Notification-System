import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from '../api';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';

export default function Login() {
  const navigate  = useNavigate();
  const { login } = useAuth();
  const showToast = useToast();

  const [form, setForm]       = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState('');

  const handleChange = (e) => {
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }));
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const data = await api.login({ email: form.email, password: form.password });
      login(data);
      showToast(`Welcome back, ${data.teacher_name}!`, 'success');
      navigate('/', { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-split">

      {/* ── Left panel — institutional identity ── */}
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
            <h1 className="login-welcome-heading">Faculty Attendance<br />Management Portal</h1>
            <p className="login-welcome-desc">
              This portal enables faculty members to monitor student attendance,
              generate low-attendance alerts, and maintain academic records in
              compliance with university regulations.
            </p>
          </div>

          {/* Info blocks */}
          <div className="login-info-grid">
            <div className="login-info-card">
              <div className="login-info-accent" />
              <div>
                <div className="login-info-label">Attendance Threshold</div>
                <div className="login-info-value">75% minimum attendance required per subject</div>
              </div>
            </div>
            <div className="login-info-card">
              <div className="login-info-accent" />
              <div>
                <div className="login-info-label">Automated Alerts</div>
                <div className="login-info-value">Email notifications dispatched to students and faculty</div>
              </div>
            </div>
            <div className="login-info-card">
              <div className="login-info-accent" />
              <div>
                <div className="login-info-label">Secure Access</div>
                <div className="login-info-value">Authenticated access for registered faculty only</div>
              </div>
            </div>
          </div>

          {/* Notice */}
          <div className="login-notice">
            <div className="login-notice-header">
              <span className="login-notice-dot" />
              System Notice
            </div>
            <p className="login-notice-text">
              Use your registered faculty email and portal password to sign in.
              Contact your department administrator if you need access.
            </p>
          </div>

          {/* Footer */}
          <div className="login-left-footer">
            Autonomous Institution — Affiliated to Visvesvaraya Technological University
          </div>

        </div>
      </div>

      {/* ── Right panel — login form ── */}
      <div className="login-right">
        <div className="login-form-card">

          <div className="login-form-header">
            <div className="login-form-logo">
              <img src="/msritlogo.png" alt="MSRIT" className="login-form-logo-img" />
              <div>
                <div className="login-form-logo-title">MSRIT</div>
                <div className="login-form-logo-sub">Attendance Portal</div>
              </div>
            </div>
            <h2 className="login-form-heading">Faculty Sign In</h2>
            <p className="login-form-subheading">Enter your credentials to continue</p>
          </div>

          {error && <div className="login-form-error">{error}</div>}

          <form onSubmit={handleSubmit} className="login-form-body">
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
                autoFocus
              />
            </div>

            <div className="login-field">
              <label className="login-label" htmlFor="password">Password</label>
              <input
                id="password"
                name="password"
                type="password"
                className="login-input"
                placeholder="Enter your password"
                value={form.password}
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
                ? <><span className="login-spinner" /> Signing in…</>
                : 'Sign In'}
            </button>
          </form>

          <p className="login-form-footer">
            Don&apos;t have an account?{' '}
            <Link to="/register" className="login-form-link">Register here</Link>
          </p>

        </div>
      </div>

    </div>
  );
}
