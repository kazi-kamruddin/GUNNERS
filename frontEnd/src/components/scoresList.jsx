import React from "react";

const ScoresList = ({ score }) => {

  return (
    <div className="whole">
      <div className="title">
        <p>{score.date}</p>
        <p>{score.competition}</p>
        <p>{score.team1}</p>
        <p>{score.team2}</p>
        <p>{score.venue}</p>
        <p>{score.form}</p>
      </div>
    </div>
  );
};

export default ScoresList;
