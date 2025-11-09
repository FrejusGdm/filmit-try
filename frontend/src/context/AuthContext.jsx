import React, { createContext, useContext, useState, useEffect } from 'react';
import { loginUser, registerUser, refreshAccessToken, logoutUser, getCurrentUser } from '../utils/authApi';
import { toast } from 'sonner';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [accessToken, setAccessToken] = useState(localStorage.getItem('access_token'));
  const [refreshToken, setRefreshToken] = useState(localStorage.getItem('refresh_token'));

  // Load user on mount if tokens exist
  useEffect(() => {
    const initAuth = async () => {
      if (accessToken) {
        try {
          const userData = await getCurrentUser(accessToken);
          setUser(userData);
        } catch (error) {
          // Token might be expired, try to refresh
          if (refreshToken) {
            try {
              const newTokens = await refreshAccessToken(refreshToken);
              setAccessToken(newTokens.access_token);
              setRefreshToken(newTokens.refresh_token);
              localStorage.setItem('access_token', newTokens.access_token);
              localStorage.setItem('refresh_token', newTokens.refresh_token);
              
              const userData = await getCurrentUser(newTokens.access_token);
              setUser(userData);
            } catch (refreshError) {
              // Refresh failed, clear everything
              logout();
            }
          } else {
            logout();
          }
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email, password) => {
    try {
      const tokens = await loginUser(email, password);
      setAccessToken(tokens.access_token);
      setRefreshToken(tokens.refresh_token);
      localStorage.setItem('access_token', tokens.access_token);
      localStorage.setItem('refresh_token', tokens.refresh_token);

      const userData = await getCurrentUser(tokens.access_token);
      setUser(userData);
      
      toast.success('Login successful!', {
        description: 'Welcome back to filmit!'
      });
      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Login failed';
      toast.error('Login failed', {
        description: errorMessage
      });
      return { success: false, error: errorMessage };
    }
  };

  const register = async (username, email, password) => {
    try {
      const tokens = await registerUser(username, email, password);
      setAccessToken(tokens.access_token);
      setRefreshToken(tokens.refresh_token);
      localStorage.setItem('access_token', tokens.access_token);
      localStorage.setItem('refresh_token', tokens.refresh_token);

      const userData = await getCurrentUser(tokens.access_token);
      setUser(userData);
      
      toast.success('Registration successful!', {
        description: 'Welcome to filmit!'
      });
      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Registration failed';
      toast.error('Registration failed', {
        description: errorMessage
      });
      return { success: false, error: errorMessage };
    }
  };

  const logout = async () => {
    try {
      if (accessToken) {
        await logoutUser(accessToken);
      }
    } catch (error) {
      // Logout anyway even if API call fails
    } finally {
      setUser(null);
      setAccessToken(null);
      setRefreshToken(null);
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('isLoggedIn');
      toast.success('Logged out successfully');
    }
  };

  const value = {
    user,
    loading,
    accessToken,
    isAuthenticated: !!user,
    login,
    register,
    logout
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
