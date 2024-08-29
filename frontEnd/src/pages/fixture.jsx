import React from "react";
import { useState, useEffect } from "react";
import '../allCss/fixture.css';
import FixtureList from '../components/fixtureList';

const Fixture = () => {
  
  const [allFixtures, setFixture] = useState(null)

  useEffect(() => {
      const fetchFixture = async () => {
          const response = await fetch('http://localhost:4000/api/fixture');
          const json = await response.json();

          if (response.ok) {
              setFixture(json)
          }
      }

      fetchFixture()
  }, [])

  return (
    <div className="fixturePage">
        <div className="pageTitle">
                Fixtures
        </div>
        <div className="allFixture">
            {allFixtures && allFixtures.map(fixture => (
                <FixtureList fixture={fixture} key={fixture._id} />
            ))}
        </div>
    </div>
  );
};

export default Fixture;