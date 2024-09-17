import { useState } from "react"
import "../allCss/signUpPage.css"
import { useSignUp } from "../hook/useSignUp"

const Signup = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const { signUp, isLoading, error } = useSignUp();

  const handleSubmit = async (e) => {
    e.preventDefault()

    console.log(email, password)
    await signUp(email,password);
  }

  const clickedLogin = () => {
    navigate('/login'); 
  };

  return (
    <body className="signup-body">
      <div className="signup-wrapper">
        <form className="signup-form" onSubmit={handleSubmit}>
          <h1>Signup</h1>
          <div className="signup-input-box">
            <input 
              type="email" 
              onChange={(e) => setEmail(e.target.value)} 
              value={email} 
              placeholder="E-mail" 
              required 
            />
          </div>
          <div className="signup-input-box">
            <input 
              type="password"
              onChange={(e) => setPassword(e.target.value)} 
              value={password} 
              placeholder="Password" 
              required
            />
          </div>
  
          
          <br />
          <button type="submit" className="signup-btn" disabled={isLoading}> Sign up </button>
          
          <div className="login-link">
            <p>
              Already have an account?{' '}
              <a href="#" onClick={clickedLogin}>Login</a>
            </p>
          </div>

          {error && <div className="error">{error}</div>}
        </form>
      </div>
    </body>
  )
}

export default Signup;

/*<form className="signup" onSubmit={handleSubmit}>
      <h3>Sign Up</h3>
      
      <label>Email address:</label>
      <input 
        type="email" 
        onChange={(e) => setEmail(e.target.value)} 
        value={email} 
      />
      <label>Password:</label>
      <input 
        type="password" 
        onChange={(e) => setPassword(e.target.value)} 
        value={password} 
      />

      <button disabled={isLoading}> Sign up </button>

      {error && <div className="error"> {error} </div>}
    </form> */