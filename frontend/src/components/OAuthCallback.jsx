import React, { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { toast } from 'sonner';
import { getCurrentUser } from '../utils/authApi';

export const OAuthCallback = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { setUser, setAccessToken, setRefreshToken } = useAuth();

  useEffect(() => {
    const handleOAuthCallback = async () => {
      const accessToken = searchParams.get('access_token');
      const refreshToken = searchParams.get('refresh_token');
      const error = searchParams.get('error');

      if (error) {
        toast.error('Authentication failed', {
          description: 'Could not sign in with Google. Please try again.'
        });
        navigate('/login');
        return;
      }

      if (!accessToken || !refreshToken) {
        toast.error('Authentication failed', {
          description: 'Invalid authentication response.'
        });
        navigate('/login');
        return;
      }

      try {
        // Store tokens
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('refresh_token', refreshToken);

        // Get user data
        const userData = await getCurrentUser(accessToken);
        
        // Update auth context (if your context exposes these setters)
        // Otherwise, this will trigger the useEffect in AuthContext
        
        toast.success('Successfully signed in!', {
          description: `Welcome, ${userData.username}!`
        });

        // Redirect to director home
        setTimeout(() => {
          navigate('/director');
        }, 500);
      } catch (error) {
        console.error('Error handling OAuth callback:', error);
        toast.error('Authentication failed', {
          description: 'Could not complete sign in. Please try again.'
        });
        navigate('/login');
      }
    };

    handleOAuthCallback();
  }, [searchParams, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center gradient-bg-dynamic">
      <div className="text-center space-y-4">
        <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto"></div>
        <p className="text-muted-foreground">Completing sign in...</p>
      </div>
    </div>
  );
};
