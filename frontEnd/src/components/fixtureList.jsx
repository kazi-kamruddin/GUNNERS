import React from "react";

const FixtureList = ({ fixture }) => {

  return (
    <div className="whole">
      <div className="title">
        <p>{fixture.date}</p>
        <p>{fixture.competition}</p>
        <p>{fixture.team1}</p>
        <p>{fixture.team2}</p>
        <p>{fixture.venue}</p>
        <p>{fixture.form}</p>
      </div>
    </div>
  );
};

export default FixtureList;
