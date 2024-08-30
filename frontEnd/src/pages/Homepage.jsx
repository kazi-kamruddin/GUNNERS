import React, { useState, useEffect } from "react";
import { useNavigate } from 'react-router-dom'; 
import "../allCss/homeStyle.css";

const Homepage = () => {
  const [allNews, setNews] = useState([]);
  const [allFixtures, setFixture] = useState([]);
  const [allScores, setScore] = useState([]);
  const navigate = useNavigate(); 

  useEffect(() => {
    const fetchNews = async () => {
      const response = await fetch('http://localhost:4000/api/news');
      const json = await response.json();

      if (response.ok) {
        setNews(json);
        //console.log(json);
      }
    }

    const fetchScore = async () => {
      const response = await fetch('http://localhost:4000/api/scores');
      const json = await response.json();

      if (response.ok) {
        setScore(json);
        //console.log(json);
      }
    }

    const fetchFixture = async () => {
      const response = await fetch('http://localhost:4000/api/fixture');
      const json = await response.json();

      if (response.ok) {
        setFixture(json);
        //console.log(json);
      }
    }

    fetchFixture();
    fetchScore();
    fetchNews();
  }, []);

  const latestNews = allNews && allNews.length > 0 ? allNews[0] : null;
  const secondLatestNews = allNews && allNews.length > 1 ? allNews[1] : null;
  const latestScore = allScores && allScores.length > 0 ? allScores[0] : null;
  const latestFixture = allFixtures && allFixtures.length > 0 ? allFixtures[0] : null;

  const clickedFirstNews = () => {
      console.log("clicked first news");
      navigate(`/news/${latestNews._id}`);
  };

  const clickedSecondNews = () => {
      console.log("clicked second news");
      navigate(`/news/${secondLatestNews._id}`);
  };

  return (
    <div className="home">
      <div className="left-column">
        <div className="news">
          {latestNews ? (
            <div 
              className="card" 
              onClick={() => clickedFirstNews()}
            >
              <div className="card-media">
                <img 
                  src={latestNews.imageLink} 
                  alt={latestNews.title}
                  className="card-image"
                />
              </div>
              <div className="card-content">
                <h3 className="card-title">{latestNews.title}</h3>
                <p className="card-body">{latestNews.body}</p>
              </div>
            </div>
          ) : (
            <p>No news available</p>
          )}
        </div>
        <div className="news">
          {secondLatestNews ? (
            <div 
              className="card" 
              onClick={() => clickedSecondNews()}
            >
              <div className="card-media">
                <img 
                  src={secondLatestNews.imageLink} 
                  alt={secondLatestNews.title}
                  className="card-image"
                />
              </div>
              <div className="card-content">
                <h3 className="card-title">{secondLatestNews.title}</h3>
                <p className="card-body">{secondLatestNews.body}</p>
              </div>
            </div>
          ) : (
            <p>No news available</p>
          )}
        </div>
      </div>
      <div className="right-column">
        <div className="score">
          {latestScore ? (
            <>
              <p>{latestScore.team1} vs {latestScore.team2}</p>
              <p>{latestScore.venue}</p>
            </>
          ) : (
            <p>No scores available</p>
          )}
        </div>
        <div className="fixture">
          {latestFixture ? (
            <>
              <p>{latestFixture.team1} vs {latestFixture.team2}</p>
              <p>{latestFixture.venue}</p>
            </>
          ) : (
            <p>No fixtures available</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Homepage;
