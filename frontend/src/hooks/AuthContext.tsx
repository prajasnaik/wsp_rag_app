import { createContext, useContext, useEffect, useState, ReactNode } from 'react';

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID;
const GOOGLE_REDIRECT_URI = import.meta.env.VITE_GOOGLE_REDIRECT_URI;
const API_BASE_URL = import.meta.env.VITE_API_URL || ''; // Get API URL from .env
const GOOGLE_AUTH_ENDPOINT = 'https://accounts.google.com/o/oauth2/v2/auth';
const GOOGLE_TOKEN_ENDPOINT = `${API_BASE_URL}/auth/google/callback`; // Backend endpoint for code exchange
const GOOGLE_REFRESH_ENDPOINT = `${API_BASE_URL}/auth/refresh`; // Backend endpoint for refresh
const AUTH_STATUS_ENDPOINT = `${API_BASE_URL}/auth/status`; // Backend endpoint for auth status
const LOGOUT_ENDPOINT = `${API_BASE_URL}/auth/logout`; // Backend endpoint for logout

interface AuthContextType {
  isAuthenticated: boolean;
  accessToken: string | null;
  isLoading: boolean;
  login: () => void;
  logout: () => void;
  checkAuth: () => Promise<boolean>;
  refresh: () => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Check for code in URL and exchange for tokens
  useEffect(() => {
    const handleInitialAuth = async () => {
      setIsLoading(true);
      
      const urlParams = new URLSearchParams(window.location.search);
      const code = urlParams.get('code');
      
      if (code) {
        // Exchange code for tokens via backend
        console.log("Exchanging authorization code for tokens");
        try {
          const response = await fetch(GOOGLE_TOKEN_ENDPOINT, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code, redirect_uri: GOOGLE_REDIRECT_URI }),
            credentials: 'include' // Include cookies in the request
          });
          
          if (response.ok) {
            const data = await response.json();
            if (data.access_token) {
              setAccessToken(data.access_token);
              setIsAuthenticated(true);
              window.history.replaceState({}, document.title, '/'); // Clean URL
            }
          } else {
            console.error("Failed to exchange code for tokens");
            setIsAuthenticated(false);
          }
        } catch (error) {
          console.error("Error during token exchange:", error);
          setIsAuthenticated(false);
        }
      } else {
        // No code in URL, check if already authenticated
        await checkAuth();
      }
      
      setIsLoading(false);
    };
    
    handleInitialAuth();
  }, []);

  // Check auth status with backend
  const checkAuth = async (): Promise<boolean> => {
    try {
      const response = await fetch(AUTH_STATUS_ENDPOINT, { 
        credentials: 'include', // Include cookies in the request
        headers: { 'Accept': 'application/json' }
      });
      
      if (response.ok) {
        const data = await response.json();
        setIsAuthenticated(data.is_authenticated);
        setAccessToken(data.access_token || null);
        return data.is_authenticated;
      } else {
        setIsAuthenticated(false);
        setAccessToken(null);
        return false;
      }
    } catch (error) {
      console.error("Error checking auth status:", error);
      setIsAuthenticated(false);
      setAccessToken(null);
      return false;
    }
  };

  // Start Google OAuth2 flow
  const login = () => {
    const params = new URLSearchParams({
      client_id: GOOGLE_CLIENT_ID,
      redirect_uri: GOOGLE_REDIRECT_URI,
      response_type: 'code',
      scope: 'profile openid email',
      access_type: 'offline',
      prompt: 'consent',
    });
    window.location.href = `${GOOGLE_AUTH_ENDPOINT}?${params.toString()}`;
  };

  // Logout
  const logout = async () => {
    try {
      await fetch(LOGOUT_ENDPOINT, { 
        method: 'POST', 
        credentials: 'include'  // Include cookies in the request
      });
      
      // Always reset auth state, even if request fails
      setIsAuthenticated(false);
      setAccessToken(null);
      
      // Redirect to home page
      window.location.href = '/';
    } catch (error) {
      console.error("Error during logout:", error);
      // Still reset auth state on error
      setIsAuthenticated(false);
      setAccessToken(null);
    }
  };

  // Token refresh logic (call before API requests if needed)
  const refresh = async (): Promise<boolean> => {
    try {
      const response = await fetch(GOOGLE_REFRESH_ENDPOINT, { 
        method: 'POST', 
        credentials: 'include' // Include cookies in the request
      });
      
      if (response.ok) {
        const data = await response.json();
        setAccessToken(data.access_token);
        setIsAuthenticated(true);
        return true;
      } else {
        setIsAuthenticated(false);
        setAccessToken(null);
        return false;
      }
    } catch (error) {
      console.error("Error refreshing token:", error);
      setIsAuthenticated(false);
      setAccessToken(null);
      return false;
    }
  };

  return (
    <AuthContext.Provider value={{ 
      isAuthenticated, 
      accessToken, 
      isLoading, 
      login, 
      logout, 
      checkAuth, 
      refresh 
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
};
