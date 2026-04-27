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
        name:             form.name,
        email:            form.email,
        portal_username:  form.portal_username,
        portal_password:  form.portal_password,
        app_password:     form.app_password,
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
    <div className="auth-page">
      <div className="auth-card auth-card-wide">
        <div className="auth-logo">
          <span className="auth-logo-icon">🎓</span>
          <div>
            <div className="auth-logo-title">MSRIT Attendance Monitor</div>
            <div className="auth-logo-sub">Department of Computer Science &amp; Engineering</div>
          </div>
        </div>

        <h2 className="auth-heading">Create teacher account</h2>

        {error && <div className="auth-error">{error}</div>}

        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label" htmlFor="name">Full name</label>
            <input
              id="name"
              name="name"
              type="text"
              className="form-input"
              placeholder="Dr. Jane Smith"
              value={form.name}
              onChange={handleChange}
              required
              autoFocus
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="email">Email address</label>
            <input
              id="email"
              name="email"
              type="email"
              className="form-input"
              placeholder="you@msrit.edu"
              value={form.email}
              onChange={handleChange}
              required
            />
          </div>

          <div className="auth-divider">Portal credentials (used by scraper)</div>

          <div className="form-group">
            <label className="form-label" htmlFor="portal_username">Portal username</label>
            <input
              id="portal_username"
              name="portal_username"
              type="text"
              className="form-input"
              placeholder="Staff portal login username"
              value={form.portal_username}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="portal_password">Portal password</label>
            <input
              id="portal_password"
              name="portal_password"
              type="password"
              className="form-input"
              placeholder="Staff portal login password"
              value={form.portal_password}
              onChange={handleChange}
              required
            />
          </div>

          <div className="auth-divider">App login password</div>

          <div className="form-group">
            <label className="form-label" htmlFor="app_password">Password</label>
            <input
              id="app_password"
              name="app_password"
              type="password"
              className="form-input"
              placeholder="Min. 6 characters"
              value={form.app_password}
              onChange={handleChange}
              required
              minLength={6}
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="app_password_confirm">Confirm password</label>
            <input
              id="app_password_confirm"
              name="app_password_confirm"
              type="password"
              className="form-input"
              placeholder="Repeat your password"
              value={form.app_password_confirm}
              onChange={handleChange}
              required
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary auth-submit-btn"
            disabled={loading}
          >
            {loading ? <><span className="spinner-sm" /> Creating account…</> : 'Create account'}
          </button>
        </form>

        <p className="auth-footer">
          Already have an account?{' '}
          <Link to="/login" className="auth-link">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
