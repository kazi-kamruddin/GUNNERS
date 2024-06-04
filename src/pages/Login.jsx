import React, { useState } from 'react';
import './Login.css';

const Login = () => {
  const [action, setAction] = useState("Login");

  const toggleAction = () => {
    setAction(action === "Login" ? "Sign Up" : "Login");
  };

  return (
    <div className='container'>
        <div className='header'>
            <div className='text'>Sign Up</div>
            <div className="underline"></div>
        </div>
        <div className="inputs">
          {action === "Login" ? <div></div> : (
            <div className="input">
                <input type="text" placeholder="Username" />
            </div>
          )}

          <div className="input">
              <input type="email" placeholder="Email" />
          </div>

          <div className="input">
              <input type="password" placeholder="Password" />
          </div>
        </div>
        {action === "Login" && (
          <div className="forgot-password">Forgot Password? <span>Click here!</span></div>
        )}

        <div className="submit-container">
            <div className={action === "Login" ? "submit gray" : "submit"} onClick={toggleAction}>Sign Up</div>
            <div className={action === "Sign Up" ? "submit gray" : "submit"} onClick={toggleAction}>Log in</div>
        </div>
    </div>
  );
};

export default Login;