import React from "react";
import '../allCss/newsDetails.css';
import { useNavigate } from "react-router-dom";

const NewsDetails = ({ news }) => {

  const navigate = useNavigate();

  const readMore = (news) => {
    navigate(`/news/${news._id}`);
  };

  return (
    <div className="whole">
      <div className="title">
        <h2>{news.title}</h2>
      </div>
      <div className="body">
        <img src={news.imageLink} alt="News" className="image" />
        <p>{news.body}</p>
      </div>
      <button className="allNewsButton" onClick={() => readMore(news)}>
          Read more &#8594;
      </button>
      <div className="footer">
        <p className="date">{new Date(news.createdAt).toLocaleDateString()}</p>
      </div>
    </div>
  );
};

export default NewsDetails;
