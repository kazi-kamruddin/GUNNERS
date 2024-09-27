import React from "react";
import { getCompLogo } from "../hook/getCompLogo";
import { getLogo } from "../hook/getClubLogo";


const ScoresList = ({ score }) => {
  return (
    <div className="score-list-whole">
      <div className="score-list-title">
        <p className="score-list-scoredate">{score.date}</p>
        <p className="score-list-venue">{score.venue}</p>
        <div className="score-list-competition">
          <img src={getCompLogo(score.competition)} alt="comp logo" className="header-comp-logo" />
        </div>
        <div className="score-grid">
          <div className="team1">
            <p className="score-list-team-name">{score.team1}</p>
            <img src={getLogo(score.team1)} alt={`${score.team1} logo`} className="single-fixture-teamLogo-itself" />
          </div>
          <div className="score">
            <p>{score.team1Score} - {score.team2Score}</p>
          </div>
          <div className="team2">
            <img src={getLogo(score.team2)} alt={`${score.team2} logo`} className="single-fixture-teamLogo-itself" />
            <p className="score-list-team-name">{score.team2}</p>
          </div>
        </div>
        <div className="scorers">
          <p className="score-list-scorer-list">Scorers: {score.team1Scorers.join(', ')}</p>
          <p className="score-list-scorer-list">Scorers: {score.team2Scorers.join(', ')}</p>
        </div>
        <p>{score.form}</p>
      </div>
    </div>
  );
};

export default ScoresList;