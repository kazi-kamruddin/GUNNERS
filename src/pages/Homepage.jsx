import React from "react";
import "./homePage/homeStyle.css";
import arsLogo from "./homePage/assets/ars.png";
import manULogo from "./homePage/assets/manu.png";
import liverLogo from "./homePage/assets/liver.png";
import matilda from "./homePage/assets/matilda.jpg";
import emirates from "./homePage/assets/emi.png";

const Homepage = () => {
  const handleClick = () => {
    window.open("https://www.arsenal.com/news/matildas-trio-named-olympic-squad", "_blank");
  };

  const handleClick2 = () => {
    window.open("https://www.arsenal.com/news/22-players-depart-arsenal-end-contacts", "_blank");
  };

  return (
    <div className="home-body">
      <h1 className="home-h1">Welcome to the home of ARSENAL</h1>
      {/* <p className="home-p">Here are some of our featured blog posts:</p> */}
      <div className="home-item-container">
        <div className="home-column home-column-1">
          <div className="blog-post">
            <img src={emirates} alt="Blog Post Image" className="blog-post-image" />
            <h2 className="blog-post-title">22 players are set to depart</h2>
            <p className="blog-post-content">Ahead of the official Premier League announcement of all men’s players who will be out of contract at their current clubs on June 30, we are taking this opportunity to thank those players leaving us at the end of the month.</p>
            <button className="blog-post-button" onClick={handleClick2} target="_blank">Read More</button>
          </div>
          <div className="blog-post">
            <img src={matilda} alt="Blog Post Image" className="blog-post-image" />
            <h2 className="blog-post-title">Matildas trio named in Olympic squad</h2>
            <p className="blog-post-content">Steph Catley, Caitlin Foord and Kyra Cooney-Cross are all heading to Paris this summer, having been named in Australia's Olympic squad.</p>
            <button className="blog-post-button" onClick={handleClick} target="_blank">Read More</button>
          </div>
        </div>
        <div className="home-column home-column-2">
          <div className="home-item home-item-small"> 
            <div className="card">
              <h2 className="card-title">Last Match Result</h2>
              <div className="card-body">
                <div className="logo-container">
                  <img src={arsLogo} alt="Team 1 Logo" className="logo" />
                  <h1 className="home-h1">4 : 1</h1>
                  <img src={manULogo} alt="Team 2 Logo" className="logoManU" />
                </div>
                <div>
                  <p className="text">Carabao Cup Final</p>
                </div>
                <div>
                  <p>Venue: Emirates Stadium, London</p>
                  <p>Attendance: 59,576</p>
                </div>
              </div>
            </div>
          </div>
          <div className="home-item home-item-small">
            <div className="card">
              <h2 className="card-title">Next Match Fixture</h2>
              <div className="card-body">
                <div className="logo-container">
                  <img src={arsLogo} alt="Team 1 Logo" className="logo" />                  
                  <h1 className="home-h1">VS</h1>
                  <img src={liverLogo} alt="Team 1 Logo" className="logoLiver" />                    
                </div>
                <div>
                  <p>Premiere League</p>
                  <p>Venue: Anfield Stadium, Liverpool</p>
                  <p>Time: 6:00 GST, 28 July, 2024</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="footer">
        <p>&copy; 2024 The Gunners</p>
      </div>
    </div>
  );
};

export default Homepage;