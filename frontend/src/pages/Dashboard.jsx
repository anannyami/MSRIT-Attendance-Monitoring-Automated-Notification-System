import { useState, useEffect, useCallback } from 'react';
import { api } from '../api';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import StudentTable from '../components/StudentTable';

export default function Dashboard() {
  const showToast = useToast();
  const { teacher } = useAuth();

  const [summary, setSummary]         = useState(null);
  const [lowStudents, setLowStudents] = useState([]);
  const [loading, setLoading]         = useState(true);
  const [sending, setSending]         = useState(false);
  const [error, setError]             = useState('');

  const [notifyTeacher, setNotifyTeacher] = useState(true);
  const [notifyStudent, setNotifyStudent] = useState(true);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const [s, students] = await Promise.all([
        api.getSummary(),
        api.getMyLowAttendance(),
      ]);
      setSummary(s);
      setLowStudents(students);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  const sendAlert = useCallback(async () => {
    if (!notifyTeacher && !notifyStudent) {
      showToast('Select at least one notification target (Teacher or Student)', 'error');
      return;
    }
    setSending(true);
    try {
      const result = await api.sendMyAlert({ notifyTeacher, notifyStudent });
      if (result.status === 'success') {
        showToast(
          `Alert sent — ${result.emails_sent} email(s) dispatched`,
          'success',
        );
      } else if (result.status === 'skipped') {
        showToast('No low-attendance students found — no email sent', 'info');
      } else if (result.status === 'partial') {
        showToast(`Partial: ${result.detail}`, 'info');
      } else {
        showToast(`Failed: ${result.detail}`, 'error');
      }
    } catch (err) {
      showToast(`Error: ${err.message}`, 'error');
    } finally {
      setSending(false);
    }
  }, [notifyTeacher, notifyStudent, showToast]);

  return (
    <div className="page-container">

      <div className="page-header">
        <h1 className="page-title">Attendance Dashboard</h1>
        <p className="page-subtitle">
          Showing attendance data for <strong>{teacher?.name}</strong>
        </p>
      </div>

      {summary && (
        <div className="stats-row">
          <div className="stat-card">
            <span className="stat-value">{summary.total_teachers}</span>
            <span className="stat-label">Teachers</span>
          </div>
          <div className="stat-card">
            <span className="stat-value">{summary.total_students}</span>
            <span className="stat-label">Students</span>
          </div>
          <div className="stat-card stat-warn">
            <span className="stat-value">{summary.low_attendance_students}</span>
            <span className="stat-label">Below {summary.threshold}%</span>
          </div>
          <div className="stat-card">
            <span className="stat-value">
              {summary.average_attendance !== null ? `${summary.average_attendance}%` : '—'}
            </span>
            <span className="stat-label">Avg Attendance</span>
          </div>
          {summary.last_scraped_at && (
            <div className="stat-card stat-info">
              <span className="stat-value stat-date">
                {new Date(summary.last_scraped_at).toLocaleDateString('en-IN')}
              </span>
              <span className="stat-label">Last Scraped</span>
            </div>
          )}
        </div>
      )}

      <div className="notify-settings-panel">
        <span className="notify-settings-label">Notify via email:</span>
        <label className="notify-checkbox-label">
          <input
            type="checkbox"
            className="notify-checkbox"
            checked={notifyTeacher}
            onChange={e => setNotifyTeacher(e.target.checked)}
          />
          <span className="notify-checkbox-text">
            <span className="notify-checkbox-icon">👨‍🏫</span>
            Teacher (summary)
          </span>
        </label>
        <label className="notify-checkbox-label">
          <input
            type="checkbox"
            className="notify-checkbox"
            checked={notifyStudent}
            onChange={e => setNotifyStudent(e.target.checked)}
          />
          <span className="notify-checkbox-text">
            <span className="notify-checkbox-icon">🎓</span>
            Students (personalized)
          </span>
        </label>
        {!notifyTeacher && !notifyStudent && (
          <span className="notify-warn-hint">Select at least one</span>
        )}
        <button
          className="btn btn-primary btn-sm"
          style={{ marginLeft: 'auto' }}
          onClick={sendAlert}
          disabled={sending || loading || (!notifyTeacher && !notifyStudent)}
        >
          {sending ? <><span className="spinner-sm" /> Sending…</> : 'Send Alert'}
        </button>
      </div>

      {error && (
        <div className="error-banner">
          Could not connect to backend: {error}
          <br /><small>Make sure the backend is running at {import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}</small>
        </div>
      )}

      <div className="student-section">
        <div className="student-section-header">
          <h2>
            Low Attendance Students
            <span className="section-teacher-name"> — {teacher?.name}</span>
          </h2>
          <p className="section-hint">Click a row to expand and view individual subject details</p>
        </div>
        <StudentTable students={lowStudents} loading={loading} />
      </div>

    </div>
  );
}
