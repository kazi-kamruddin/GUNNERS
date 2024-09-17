import React from "react";
import '../allCss/newsDetails.css';
import { useNavigate } from "react-router-dom";

const NewsDetails = ({ news }) => {
  const navigate = useNavigate();

  const handleNavigate = () => {
    navigate(`/news/${news._id}`);
  };

  return (
    <div className="news-card" onClick={handleNavigate}>
      <div className="news-image-container">
        <img src={news.imageLink} alt={news.title} className="news-image" />
        <div className="news-title-overlay">
          <h2>{news.title}</h2>
        </div>
      </div>
    </div>
  );
};

export default NewsDetails;
