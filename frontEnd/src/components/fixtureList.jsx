import React from "react";

const FixtureList = ({ fixture }) => {

  return (
    <div className="whole">
      <div className="title">
        <p>{fixture.date}</p>
        <p>{fixture.competition}</p>
        <p>{fixture.team}</p>
        <img src={fixture.team1Logo} alt="team1" className="image1" />
        <p>{fixture.team2}</p>
        <img src={fixture.team2Logo} alt="team2" className="image2" />
        <p>{fixture.venue}</p>
        <p>{fixture.form}</p>
      </div>
    </div>
  );
};

export default FixtureList;
