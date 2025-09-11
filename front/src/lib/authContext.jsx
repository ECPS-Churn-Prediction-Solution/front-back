import React, { createContext, useCallback, useContext, useEffect, useState } from 'react';
import { apiFetch } from './api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const HINT_KEY = 'auth-has-session';

  const setAuthData = useCallback((newUser) => {
    setUser(newUser);
    if (newUser) {
      localStorage.setItem(HINT_KEY, '1');
    } else {
      localStorage.removeItem(HINT_KEY);
    }
  }, []);

  const refresh = useCallback(async () => {
    try {
      const me = await apiFetch('/api/users/me', { silent401: true });
      setAuthData(me);
    } catch (e) {
      setAuthData(null);
    } finally {
      setLoading(false);
    }
  }, [setAuthData]);

  useEffect(() => {
    const hasHint = localStorage.getItem(HINT_KEY) === '1';
    if (hasHint) {
      refresh();
    } else {
      setLoading(false);
    }
  }, [refresh]);

  const login = useCallback(async (email, password) => {
    const res = await apiFetch('/api/users/login', {
      method: 'POST',
      body: { email, password },
    });
    setAuthData(res.user);
    return res.user;
  }, [setAuthData]);

  const register = useCallback(async (payload) => {
    await apiFetch('/api/users/register', {
      method: 'POST',
      body: payload,
    });
    return true;
  }, []);

  const logout = useCallback(async () => {
    await apiFetch('/api/users/logout', { method: 'POST' });
    setAuthData(null);
  }, [setAuthData]);

  const value = { user, loading, refresh, login, register, logout, setAuthData };
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
