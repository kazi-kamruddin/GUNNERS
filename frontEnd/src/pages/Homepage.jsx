import React, { useState, useEffect } from "react";
import "../allCss/homeStyle.css";

const Homepage = () => {
  const [allNews, setNews] = useState([]);
  const [allFixtures, setFixture] = useState([]);
  const [allScores, setScore] = useState([]);

  useEffect(() => {
    const fetchNews = async () => {
      const response = await fetch('http://localhost:4000/api/news');
      const json = await response.json();

      if (response.ok) {
        setNews(json);
        console.log(json);
      }
    }

    const fetchScore = async () => {
      const response = await fetch('http://localhost:4000/api/scores');
      const json = await response.json();

      if (response.ok) {
        setScore(json);
        console.log(json);
      }
    }

    const fetchFixture = async () => {
      const response = await fetch('http://localhost:4000/api/fixture');
      const json = await response.json();

      if (response.ok) {
        setFixture(json);
        console.log(json);
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

  return (
    <div className="home">
      <div className="left-column">
        <div className="news1">
          {latestNews ? (
            <>
              <p>{latestNews.title}</p>
              <p>{latestNews.body}</p>
            </>
          ) : (
            <p>No news available</p>
          )}
        </div>
        <div className="news2">
          {secondLatestNews ? (
            <>
              <p>{secondLatestNews.title}</p>
              <p>{secondLatestNews.body}</p>
            </>
          ) : (
            <p>No more news available</p>
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
