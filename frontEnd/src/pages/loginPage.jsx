import { useState } from "react";
import { useLogin } from "../hook/useLogin";
import "../allCss/Login.css";
import { useNavigate } from 'react-router-dom';

const Login = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false); // State for toggling password visibility
  const { login, isLoading, error } = useLogin();

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log(email, password);
    await login(email, password);
  };

  const clickedRegister = () => {
    navigate('/signUp'); 
  };

  return (
    <body className="login-body">
      <div className="wrapper">
        <form className="login-form" onSubmit={handleSubmit}>
          <h1>Login</h1>
          <div className="input-box">
            <input 
              type="email" 
              onChange={(e) => setEmail(e.target.value)} 
              value={email} 
              placeholder="E-mail" 
              required 
            />
          </div>
          <div className="input-box">
            <input 
              type={showPassword ? "text" : "password"} // Toggle between text and password
              onChange={(e) => setPassword(e.target.value)} 
              value={password} 
              placeholder="Password" 
              required
            />
            <div className="show-password">
              <input 
                type="checkbox" 
                checked={showPassword}
                onChange={() => setShowPassword(!showPassword)}
              />
              <p>Show Password</p>
            </div>
          </div>
  
          <br />
          <button type="submit" className="btn" disabled={isLoading}>Login</button>
          
          <div className="signup-link">
            <p>
              Don't have an account?{' '}
              <a href="#" onClick={clickedRegister}>Register</a>
            </p>
          </div>

          {error && <div className="error">{error}</div>}
        </form>
      </div>
    </body>
  );
};

export default Login;
