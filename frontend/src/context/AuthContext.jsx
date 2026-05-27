import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const storedToken = localStorage.getItem('heartguard_token');
    const storedUser = localStorage.getItem('heartguard_user');

    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));

      api.get('/auth/me')
        .then((res) => {
          const userData = res.data;
          setUser(userData);
          localStorage.setItem('heartguard_user', JSON.stringify(userData));
        })
        .catch(() => {
          localStorage.removeItem('heartguard_token');
          localStorage.removeItem('heartguard_user');
          setToken(null);
          setUser(null);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = useCallback(async (email, password) => {
    const res = await api.post('/auth/login', { email, password });
    const { access_token, user: userData } = res.data;
    localStorage.setItem('heartguard_token', access_token);
    localStorage.setItem('heartguard_user', JSON.stringify(userData));
    setToken(access_token);
    setUser(userData);
    return userData;
  }, []);

  const register = useCallback(async (email, password, fullName) => {
    const res = await api.post('/auth/register', {
      email,
      password,
      full_name: fullName
    });
    const { access_token, user: userData } = res.data;
    localStorage.setItem('heartguard_token', access_token);
    localStorage.setItem('heartguard_user', JSON.stringify(userData));
    setToken(access_token);
    setUser(userData);
    return userData;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('heartguard_token');
    localStorage.removeItem('heartguard_user');
    setToken(null);
    setUser(null);
    navigate('/');
  }, [navigate]);

  const value = {
    user,
    token,
    loading,
    isAuthenticated: !!token,
    login,
    register,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export default AuthContext;
