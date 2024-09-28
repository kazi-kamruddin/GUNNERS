import React from 'react';
import { Link } from 'react-router-dom';
import '../allCss/newsNavBar.css'; 

const NewsNavBar = () => {
    return (
        <nav className="news-nav-bar">
            <div className="nav-links">
                <Link to="/news/men" className="nav-link men-news">Men</Link>
                <Link to="/news/women" className="nav-link women-news">Women</Link>
                <Link to="/news/youth" className="nav-link youth-news">Academy</Link>
            </div>
        </nav>
    );
};

export default NewsNavBar;
