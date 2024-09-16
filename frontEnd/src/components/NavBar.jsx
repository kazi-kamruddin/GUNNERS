import React from "react";
import config from "../config";
import { Link } from "react-router-dom";
import { useLocation } from "react-router-dom";
import { useLogout } from "../hook/useLogout";
import { useAuthContext } from "../hook/useAuthContext";
import '../allCss/NavBar.css';

const NavBar = () => {
  const { logout } = useLogout();
  const { user } = useAuthContext();
  
  let isAdmin = false;
  let location = useLocation();

  const handleLogout = () => {
    logout();
  };

  if (user && user.email === config.ADMIN_EMAIL) {
    isAdmin = true;
  } else if (user) {
    isAdmin = false;
  } else {
    isAdmin = false;
  }

  const showSidebar = () => {
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
      sidebar.style.display = 'flex';
    }
  };

  const hideSidebar = () => {
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
      sidebar.style.display = 'none';
    }
  };

  return (
    <nav>

      <ul className="sidebar">
        <li onClick={hideSidebar}>
          <a href="#"><svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e8eaed">
            <path d="m256-200-56-56 224-224-224-224 56-56 224 224 224-224 56 56-224 224 224 224-56 56-224-224-224 224Z"/></svg>
          </a>
        </li>
        <li><Link to="/">Home</Link></li>
        {user && isAdmin && <li><Link to="/adminDashboard">Admin Dashboard</Link></li>}
        <li><Link to="/teams">Teams</Link></li>
        <li><Link to="/fixture">Fixtures</Link></li>
        <li><Link to="/scores">Scores</Link></li>
        <li><Link to="/achievements">Achievements</Link></li>
        <li><Link to="/news">News</Link></li>
        {!user && <li><Link to="/login">Login</Link></li>}
        {!user && <li><Link to="/signUp">Signup</Link></li>}
        {user && <li><button onClick={handleLogout}>Logout</button></li>}
      </ul>

      <ul>
        <li><Link to="/">Arsenal</Link></li>
        <li className={`hideOnMobile ${location.pathname === "/" && "active"}`}><Link to="/">Home</Link></li>
        {user && isAdmin && (
          <li className={`hideOnMobile ${location.pathname === "/adminDashboard" && "active"}`}>
            <Link to="/adminDashboard">Admin Dashboard</Link>
          </li>
        )}
        <li className={`hideOnMobile ${location.pathname === "/teams" && "active"}`}><Link to="/teams">Teams</Link></li>
        <li className={`hideOnMobile ${location.pathname === "/fixture" && "active"}`}><Link to="/fixture">Fixtures</Link></li>
        <li className={`hideOnMobile ${location.pathname === "/scores" && "active"}`}><Link to="/scores">Scores</Link></li>
        <li className={`hideOnMobile ${location.pathname === "/achievements" && "active"}`}><Link to="/achievements">Achievements</Link></li>
        <li className={`hideOnMobile ${location.pathname === "/news" && "active"}`}><Link to="/news">News</Link></li>
        {!user && (
          <>
            <li className={`hideOnMobile ${location.pathname === "/login" && "active"}`}><Link to="/login">Login</Link></li>
            <li className={`hideOnMobile ${location.pathname === "/signUp" && "active"}`}><Link to="/signUp">Signup</Link></li>
          </>
        )}
        {user && (
          <li className="hideOnMobile">
            <button onClick={handleLogout}>Logout</button>
          </li>
        )}

        <li className="drawer" onClick={showSidebar}>
          <a href="#">
            <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e8eaed">
              <path d="M120-240v-80h720v80H120Zm0-200v-80h720v80H120Zm0-200v-80h720v80H120Z" />
            </svg>
          </a>
        </li>
      </ul>
    </nav>
  );
};

export default NavBar;
