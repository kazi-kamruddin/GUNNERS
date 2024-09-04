import React, { useState, useEffect } from "react";
import { useNavigate } from 'react-router-dom'; 
import { getLogo } from "../hook/getClubLogo";
import { getCompLogo } from "../hook/getCompLogo";
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

  const clickedAllFixture = () => {
    console.log("clicked all fixture");
    navigate(`/fixture`);
  };

  const clickedAllScore = () => {
    console.log("clicked all score");
    navigate(`/scores`);
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
      <div className="fixture">
          {latestFixture ? (
            <div className="fixture-card">
              <div className="fixture-date">  
                   Upcoming match on {latestFixture.date}
              </div>
              <div className="fixture-teams">
                  <div className="team-name">
                      <img src={getLogo(latestFixture.team1)} alt={`${latestFixture.team2} logo`} className="team-logo"/>
                      {latestFixture.team1}
                  </div>
                  <div className="versus">VS</div>
                  <div className="team-name">
                      <img src={getLogo(latestFixture.team2)} alt={`${latestFixture.team2} logo`} className="team-logo"/>
                      {latestFixture.team2}
                  </div>
              </div>
              <div className="fixture-competition">
                    <img src={getCompLogo(latestFixture.competition)} alt={`${latestFixture.competition} logo`} className="competition-logo"/>
                    <div className="competition-name">
                    </div>
              </div>
              <div className="fixture-venue">
                    Venue : &nbsp;{latestFixture.venue}
              </div>
              <button className="go-to-all-fixture" onClick={() => clickedAllFixture()}>
                  Explore all the fixtures &#x27A1;
              </button>
            </div>
          ) : (
            <p>No fixtures available</p>
          )}
        </div>
        <div className="score">
          {latestScore ? (
            <div className="score-card">
              <div className="score-date">  
                   {latestScore.date}
              </div>
              <div className="score-teams">
                  <div className="team-name">
                      <img src={getLogo(latestScore.team1)} alt={`${latestScore.team2} logo`} className="team-logo"/>
                      {latestScore.team1}
                  </div>
                  <div className="result">
                      {latestScore.team1Score}-{latestScore.team2Score}
                  </div>
                  <div className="team-name">
                      <img src={getLogo(latestScore.team2)} alt={`${latestScore.team2} logo`} className="team-logo"/>
                      {latestScore.team2}
                  </div>
              </div>
              <div className="score-competition">
                    <img src={getCompLogo(latestScore.competition)} alt={`${latestScore.competition} logo`} className="competition-logo"/>
                    <div className="competition-name">
                    </div>
              </div>
              <div className="score-venue">
                    Venue : &nbsp;{latestScore.venue}
              </div>
              <button className="go-to-all-score" onClick={() => clickedAllScore()}>
                  Explore all the scores &#x27A1;
              </button>
            </div>
          ) : (
            <p>No fixtures available</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Homepage;
