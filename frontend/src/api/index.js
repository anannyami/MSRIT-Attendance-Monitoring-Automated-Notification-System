const BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

function getToken() {
  return localStorage.getItem('msrit_token');
}

async function request(path, options = {}) {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  const res = await fetch(`${BASE}${path}`, { ...options, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export const api = {
  // ── Auth ─────────────────────────────────────────────────────────────────
  login: ({ email, password }) =>
    request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),

  register: ({ name, email, portal_username, portal_password, app_password }) =>
    request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ name, email, portal_username, portal_password, app_password }),
    }),

  // ── Me (authenticated teacher's own data) ─────────────────────────────────
  getMyStudents: (semester) => {
    const p = semester ? `?semester=${encodeURIComponent(semester)}` : '';
    return request(`/me/students${p}`);
  },

  getMyLowAttendance: () =>
    request('/me/low-attendance'),

  sendMyAlert: ({ notifyTeacher = true, notifyStudent = true } = {}) =>
    request('/me/alerts/send', {
      method: 'POST',
      body: JSON.stringify({ notify_teacher: notifyTeacher, notify_student: notifyStudent }),
    }),

  // ── Legacy (admin, backward-compatible) ──────────────────────────────────
  getTeachers: () =>
    request('/teachers'),

  getSummary: () =>
    request('/summary'),

  getLowAttendance: (teacherId) =>
    request(`/low-attendance?teacher_id=${teacherId}`),

  sendAlert: (teacherId, { notifyTeacher = true, notifyStudent = true } = {}) =>
    request(`/alerts/send/${teacherId}`, {
      method: 'POST',
      body: JSON.stringify({ notify_teacher: notifyTeacher, notify_student: notifyStudent }),
    }),

  getLogs: ({ teacher_email, usn, status, limit = 200, skip = 0 } = {}) => {
    const p = new URLSearchParams({ limit, skip });
    if (teacher_email) p.append('teacher_email', teacher_email);
    if (usn)           p.append('usn', usn);
    if (status)        p.append('status', status);
    return request(`/alerts/logs?${p}`);
  },
};
