import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';

export default function Navbar() {
  const { isAuthenticated, teacher, logout } = useAuth();
  const navigate  = useNavigate();
  const showToast = useToast();

  const handleLogout = () => {
    logout();
    showToast('You have been signed out', 'info');
    navigate('/login', { replace: true });
  };

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <img src="/msritlogo.png" alt="MSRIT" className="navbar-logo-img" />
        <div className="navbar-title">
          <span className="navbar-name">MSRIT Attendance Monitor</span>
          <span className="navbar-sub">Department of Computer Science &amp; Engineering</span>
        </div>
      </div>

      {isAuthenticated ? (
        <div className="navbar-right">
          <div className="navbar-links">
            <NavLink to="/" end className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
              Dashboard
            </NavLink>
            <NavLink to="/logs" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
              Alert Logs
            </NavLink>
          </div>
          <div className="navbar-user">
            <span className="navbar-user-name">{teacher?.name}</span>
            <button className="navbar-logout-btn" onClick={handleLogout}>
              Sign out
            </button>
          </div>
        </div>
      ) : (
        <div className="navbar-links">
          <NavLink to="/login" className="nav-link">
            Sign in
          </NavLink>
        </div>
      )}
    </nav>
  );
}
