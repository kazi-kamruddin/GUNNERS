import React from "react";

const ScoresList = ({ score }) => {

  return (
    <div className="whole">
      <div className="title">
        <p>{score.date}</p>
        <p>{score.competition}</p>
        <p>{score.team1}</p>
        <img src={score.team1Logo} alt="team1" className="image1" />
        <p>{score.team2}</p>
        <img src={score.team2Logo} alt="team2" className="image2" />
        <p>{score.venue}</p>
        <p>{score.form}</p>
      </div>
    </div>
  );
};

export default ScoresList;
