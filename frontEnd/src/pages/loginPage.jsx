import { useState } from "react";
import { useLogin } from "../hook/useLogin";
import "../allCss/Login.css";

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login, isLoading, error } = useLogin();

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log(email, password);
    await login(email, password);
  }

  return (

    <body className="login-body">

      <div className="wrapper">
        <form className="login" onSubmit={handleSubmit}>
          <h1>Login</h1>
          <div className="input-box">
            <input type="email" 
            onChange={(e) => setEmail(e.target.value)} 
            value={email} 
            placeholder="E-mail" required />
            

          </div>
          <div className="input-box">
            <input type="password"
              onChange={(e) => setPassword(e.target.value)} 
              value={password} 
              placeholder="Password" required/>

          </div>
  
          <a href="#"> Forgot Password? </a>
          
          <br/>
          <button type="submit" className="btn" disabled={isLoading}>Login</button>
          <div className="signup-link">
            <p>Don't have an account?<a href = "#">Register</a></p>
          </div>
          {error && <div className="error">{error}</div>}
  
        </form>
      </div>
        
    </body>


    /*<div className="wrapper">
      <h1>Log In</h1>
      <form className="login" onSubmit={handleSubmit}>
        

        <label>Email address:</label>
        <input 
          type="email" 
          onChange={(e) => setEmail(e.target.value)} 
          value={email} 
        />
        <br />

        <label>Password:</label>
        <input 
          type="password" 
          onChange={(e) => setPassword(e.target.value)} 
          value={password} 
        />
        <br />

        <button disabled={isLoading}>Log in</button>

        {error && <div className="error">{error}</div>}
      </form>
    </div>*/
  );
}

export default Login;
