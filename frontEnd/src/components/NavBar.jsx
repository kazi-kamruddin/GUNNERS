import React from "react";
import { Link } from "react-router-dom";
import { useLocation } from "react-router-dom";
import './NavBar.css';
import { useLogout } from "../hook/useLogout";
import { useAuthContext } from "../hook/useAuthContext";

const NavBar = () => {
  let location = useLocation();

  const { logout } = useLogout();
  const { user } = useAuthContext();

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="nav-main-div">
      <nav className="navigationBar">
        <div className={`nav-item ${location.pathname === "/" && "active"}`}>
          <Link to="/">Home</Link>
        </div>
        { user && (
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
