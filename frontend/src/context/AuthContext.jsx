import { createContext, useContext, useState, useCallback } from 'react';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('msrit_token'));
  const [teacher, setTeacher] = useState(() => {
    try {
      const stored = localStorage.getItem('msrit_teacher');
      return stored ? JSON.parse(stored) : null;
    } catch {
      localStorage.removeItem('msrit_teacher');
      return null;
    }
  });

  const login = useCallback((tokenData) => {
    const teacherData = {
      id:    tokenData.teacher_id,
      name:  tokenData.teacher_name,
      email: tokenData.teacher_email,
    };
    localStorage.setItem('msrit_token', tokenData.access_token);
    localStorage.setItem('msrit_teacher', JSON.stringify(teacherData));
    setToken(tokenData.access_token);
    setTeacher(teacherData);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('msrit_token');
    localStorage.removeItem('msrit_teacher');
    setToken(null);
    setTeacher(null);
  }, []);

  return (
    <AuthContext.Provider value={{ token, teacher, login, logout, isAuthenticated: !!token }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
