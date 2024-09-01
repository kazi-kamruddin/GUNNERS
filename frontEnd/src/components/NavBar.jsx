import React from "react";
import config from "../config";
import { Link } from "react-router-dom";
import { useLocation } from "react-router-dom";
import '../allCss/NavBar.css';
import { useLogout } from "../hook/useLogout";
import { useAuthContext } from "../hook/useAuthContext";

const NavBar = () => {
  let location = useLocation();

  const { logout } = useLogout();
  const { user } = useAuthContext();
  
  let isAdmin = false;

  const handleLogout = () => {
    logout();
  };

  if(user && user.email === config.ADMIN_EMAIL){
      console.log('admin detected');
      isAdmin = true;
  }
  else if(user){
    console.log('general user detected');
    isAdmin = false;
  }
  else {
    console.log('no user detected');
    isAdmin = false;
  }

  return (
    <div className="nav-main-div">
      <nav className="navigationBar">
        { user && isAdmin && (
            <div className="admin-dash">
              <Link to="/adminDashboard">Admin Dashboard</Link>
            </div>
        )}
        <div className={`nav-item ${location.pathname === "/" && "active"}`}>
          <Link to="/">Home</Link>
        </div>
        { user && !isAdmin && (
            <div className={`nav-item ${location.pathname === "/dashboard" && "active"}`}>
              <Link to="/dashboard">Dashboard</Link>
            </div>
        )}
        <div className={`nav-item ${location.pathname === "/teams" && "active"}`}>
          <Link to="/teams">Teams</Link>
        </div>
        <div className={`nav-item ${location.pathname === "/shop" && "active"}`}>
          <Link to="/shop">Shops</Link>
        </div>
        <div className={`nav-item ${location.pathname === "/fixture" && "active"}`}>
          <Link to="/fixture">Fixture</Link>
        </div>
        <div className={`nav-item ${location.pathname === "/scores" && "active"}`}>
          <Link to="/scores">Scores</Link>
        </div>
        <div className={`nav-item ${location.pathname === "/news" && "active"}`}>
          <Link to="/news">News</Link>
        </div>
        { !user && (
            <div className={`nav-item ${location.pathname === "/login" && "active"}`}>
              <Link to="/login">Login</Link>
            </div>
        )}
        { !user && (
            <div className={`nav-item ${location.pathname === "/signUp" && "active"}`}>
              <Link to="/signUp">SignUp</Link>
            </div>
        )}
        { user && (
            <div className="nav-item">
              <button className="logout" onClick={handleLogout}>Logout</button>
            </div>
        )}
      </nav>
    </div>
  );
};

export default NavBar;
