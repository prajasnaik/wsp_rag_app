import React from 'react';
import { TbHexagonLetterP } from "react-icons/tb";
import { useAuth } from '../../hooks/AuthContext';
import './Login.css';

const Login: React.FC = () => {
  const { login } = useAuth();

  return (
    <div className="login-container">
      <TbHexagonLetterP className="ai-icon" />
      <h1>Sign in to continue</h1>
      <button className="google-login-btn" onClick={login}>
        <img src="https://developers.google.com/identity/images/g-logo.png" alt="Google logo" className="google-logo" />
        Login with Google
      </button>
    </div>
  );
};

export default Login;
