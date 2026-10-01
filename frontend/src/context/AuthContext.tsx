import React, { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import axiosClient from '../api/axiosClient';
import { useNavigate } from 'react-router-dom';

export type UserRole = 'admin' | 'lecturer' | null;

interface User {
  id: number;
  email: string;
  role: UserRole;
  is_active: boolean;
}

interface AuthContextType {
  user: User | null;
  role: UserRole;
  token: string | null;
  login: (token: string, user_data: User) => void;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [role, setRole] = useState<UserRole>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    if (token) {
      axiosClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchUser();
    } else {
      delete axiosClient.defaults.headers.common['Authorization'];
      setIsLoading(false);
    }
  }, [token]);

  const fetchUser = async () => {
    try {
      const response = await axiosClient.get('/auth/me');
      setUser(response.data);
      setRole(response.data.role);
    } catch (error) {
      console.error("Failed to fetch user", error);
      logout();
    } finally {
      setIsLoading(false);
    }
  };

  const login = (newToken: string, user_data: User) => {
    localStorage.setItem('token', newToken);
    setToken(newToken);
    setUser(user_data);
    setRole(user_data.role);
    axiosClient.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    setRole(null);
    delete axiosClient.defaults.headers.common['Authorization'];
    navigate('/login');
  };

  return (
    <AuthContext.Provider value={{ user, role, token, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
