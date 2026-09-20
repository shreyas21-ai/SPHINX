import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('sphinx_access_token');
      if (token) {
        try {
          const response = await api.get('/auth/me');
          if (response.data?.status === 'success') {
            setUser(response.data.data);
          }
        } catch (err) {
          console.error("Auth initialization failed:", err);
          logout();
        }
      }
      setLoading(false);
    };
    checkAuth();
  }, []);

  const login = async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    if (response.data?.status === 'success') {
      const { access_token, refresh_token, user: userData } = response.data.data;
      localStorage.setItem('sphinx_access_token', access_token);
      localStorage.setItem('sphinx_refresh_token', refresh_token);
      localStorage.setItem('sphinx_user', JSON.stringify(userData));
      setUser(userData);
      return userData;
    }
    throw new Error(response.data?.message || 'Login failed');
  };

  const logout = () => {
    localStorage.removeItem('sphinx_access_token');
    localStorage.removeItem('sphinx_refresh_token');
    localStorage.removeItem('sphinx_user');
    localStorage.removeItem('sphinx_access_purpose');
    setUser(null);
  };

  const role = user?.role || 'GUEST';

  return (
    <AuthContext.Provider value={{ user, role, loading, isAuthenticated: !!user, login, logout, setUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
