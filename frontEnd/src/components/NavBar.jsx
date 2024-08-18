import React from "react";
import { Link } from "react-router-dom";
import { useLocation } from "react-router-dom";
import './NavBar.css';
import { useLogout } from "../hook/useLogout";


const pages = [
  { link: "/", text: "Home" },
  { link: "/dashboard", text: "Dashboard" },
  { link: "/teams", text: "Teams" },
  { link: "/shop", text: "Shops" },
  { link: "/news", text: "News" },
  { link: "/login", text: "Login" },
  { link: "/signUp", text: "SignUp" },
];

const NavBar = () => {
  let location = useLocation();

  const {logout} = useLogout();

  const handleLogout = () => {
    logout();
  }

  return (
    <div className="nav-main-div">
      <nav>
        <ul className="nav-ul">
          {pages.map((item, idx) => {
            return (
              <li key={idx} className={`nav-item ${location.pathname === item.link && "active"}`}>
                <Link to={item.link}>{item.text}</Link>
              </li>
            );
          })}
          <div>
              <button className="logout" onClick={handleLogout}> logout </button>
          </div>
        </ul>
      </nav>
    </div>
  );
};

export default NavBar;
