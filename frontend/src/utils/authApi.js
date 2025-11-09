import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const authApi = axios.create({
  baseURL: `${API_BASE_URL}/api/auth`,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Login user
export const loginUser = async (email, password) => {
  const response = await authApi.post('/login', { email, password });
  return response.data;
};

// Register user
export const registerUser = async (username, email, password) => {
  const response = await authApi.post('/register', { username, email, password });
  return response.data;
};

// Refresh access token
export const refreshAccessToken = async (refreshToken) => {
  const response = await authApi.post('/refresh', { refresh_token: refreshToken });
  return response.data;
};

// Get current user
export const getCurrentUser = async (accessToken) => {
  const response = await axios.get(`${API_BASE_URL}/api/auth/me`, {
    headers: {
      Authorization: `Bearer ${accessToken}`
    }
  });
  return response.data;
};

// Logout user
export const logoutUser = async (accessToken) => {
  const response = await axios.post(`${API_BASE_URL}/api/auth/logout`, {}, {
    headers: {
      Authorization: `Bearer ${accessToken}`
    }
  });
  return response.data;
};
