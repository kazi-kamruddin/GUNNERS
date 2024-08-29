import React from "react";
import "../allCss/homeStyle.css";

const Homepage = () => {
  return (
    <div className="home">
      <div className="left-column">
        <div className="news1">
            <p>first news</p>
            <p>second line</p>
        </div>
        <div className="news2">
            <p>second news</p>
            <p>second line</p>
        </div>
      </div>
      <div className="right-column">
        <div className="score">Latest Score</div>
        <div className="fixture">Next Fixture</div>
      </div>
    </div>
  );
};

export default Homepage;
