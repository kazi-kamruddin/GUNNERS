import React from "react";
import { Link } from "react-router-dom";
import { useLocation } from "react-router-dom";
import './NavBar.css';


const pages = [
  { link: "/", text: "Home" },
  { link: "/dashboard", text: "Dashboard" },
  { link: "/login", text: "Login" },
  { link: "/teams", text: "Teams" },
  { link: "/shop", text: "Shops" },
];

const NavBar = () => {
  let location = useLocation();

  return (
    <div className="nav-main-div">
      <nav>
        <ul className="nav-ul">
          {pages.map((item, idx) => {
            return (
              <li
                key={idx}
                className={`nav-item ${
                  location.pathname === item.link && "active"
                }`}
              >
                <Link to={item.link}>{item.text}</Link>
              </li>
            );
          })}
        </ul>
      </nav>
    </div>
  );
};

export default NavBar;
