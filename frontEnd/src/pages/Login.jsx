import React, { useState } from 'react';
import '../allCss/Login.css';

const Login = () => {
  const [action, setAction] = useState("Login");
  const [backgroundImage, setBackgroundImage] = useState("https://wallpapers.com/images/hd/fanart-for-pierre-emerick-aubameyang-from-arsenal-fc-7kp14rmfc8zr68yx.jpg");

  const toggleAction = () => {
    setAction(prevAction => (prevAction === "Login" ? "Sign Up" : "Login"));
    // ekhane change hbe bg
    setBackgroundImage(prevBackground => (
      prevBackground === "https://wallpapers.com/images/hd/fanart-for-pierre-emerick-aubameyang-from-arsenal-fc-7kp14rmfc8zr68yx.jpg" 
      ? "https://cdn.wallpapersafari.com/53/52/KjNu1B.png" 
      : "https://wallpapers.com/images/hd/fanart-for-pierre-emerick-aubameyang-from-arsenal-fc-7kp14rmfc8zr68yx.jpg"
    ));
  };

  return (
    <div className='login-background' style={{ backgroundImage: `url(${backgroundImage})` }}>
      <div className='container'>
          <div className='header'>
              <div className='text'>{action}</div>
              <div className="underline"></div>
          </div>
          <div className="inputs">
            {action === "Login" ? <div></div> : (
              <div className="input">
                  <img src="https://mir-s3-cdn-cf.behance.net/project_modules/disp/41b3cb23122177.5631e11bb8892.png" alt="" />
                  <input type="text" placeholder="Username" />
              </div>
            )}

            <div className="input">
                <img src="https://cdn.dribbble.com/users/4874/screenshots/3074660/media/f0ff54c0c250bca686a89c7b39b83139.gif" alt="" /> 
                <input type="email" placeholder="Email" />
            </div>

            <div className="input">
                <img src="https://cdn-icons-png.flaticon.com/512/421/421648.png" alt="" /> 
                <input type="password" placeholder="Password" />
            </div>
          </div>

          
          <div className="submit-container">
              <div className="submit" style={{ backgroundColor: '#33691E' }}>Submit</div>
          </div>

          {action === "Login" && (
            <div className="forgot-password">Forgot Password? <span>Click here!</span></div>
          )}
          
          
          <div className="submit-container">
              <div className={action === "Login" ? "submit gray" : "submit"} onClick={toggleAction}>Sign Up</div>
              <div className={action === "Sign Up" ? "submit gray" : "submit"} onClick={toggleAction}>Log in</div>
          </div>
      </div>
    </div>
  );
};

export default Login;
