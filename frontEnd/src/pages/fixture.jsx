import React, { useState, useEffect } from "react";
import '../allCss/fixture.css';
import { getCompLogo } from "../hook/getCompLogo";
import { getLogo } from "../hook/getClubLogo";

const Fixture = () => {
  const [allFixtures, setFixture] = useState(null);

  useEffect(() => {
    const fetchFixture = async () => {
      const response = await fetch('http://localhost:4000/api/fixture');
      const json = await response.json();

      if (response.ok) {
        setFixture(json);
      }
    };

    fetchFixture();
  }, []);

  const FixtureList = ({ fixture }) => {
    const opponent = (fixture.team1 === "ARSENAL" || fixture.team1 === "arsenal" || fixture.team1 === "Arsenal") ? fixture.team2 : fixture.team1;

    const formResults = fixture.form.split('').map((result, index) => (
      <div key={index} className={`form-result ${result.toLowerCase()}`}>
        {result}
      </div>
    ));

    return (
      <div className="single-fixture-card">
        <div className="single-fixture-info">
          <div className="info-header">
            <div className="header-text">
              <div className="match-date">{fixture.date}</div>
              <div className="match-venue">Venue : {fixture.venue}</div>
            </div>
            <div className="header-image">
              <img src={getCompLogo(fixture.competition)} alt="comp logo" className="header-comp-logo" />
            </div>
          </div>
          <div className="info-body">
            <div className="single-fixture-team-name">{fixture.team1}</div>
            <div className="single-fixture-team-logo">
              <img src={getLogo(fixture.team1)} alt="team logo" className="single-fixture-teamLogo-itself" />
            </div>
            <div className="single-fixture-versus">VS</div>
            <div className="single-fixture-team-logo">
              <img src={getLogo(fixture.team2)} alt="team logo" className="single-fixture-teamLogo-itself" />
            </div>
            <div className="single-fixture-team-name">{fixture.team2}</div>
          </div>
          <div className="single-fixture-form">
            <div className="form-text">Recent form :   </div>
            <div className="form-results">
              {formResults}
            </div>
          </div>
          <div className="extender"></div>
        </div>
      </div>
    );
  };

  return (
    <div className="fixture-page">
      <div className="title">
        Fixtures
      </div>

      <div className="all-fixtures">
        {allFixtures ? (
          allFixtures.map(fixture => (
            <FixtureList fixture={fixture} key={fixture._id} />
          ))
        ) : (
          <div className="err">
            <p>No fixtures available</p>
            <p>No fixtures available</p>
            <p>No fixtures available</p>
            <p>No fixtures available</p>
            <p>No fixtures available</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Fixture;