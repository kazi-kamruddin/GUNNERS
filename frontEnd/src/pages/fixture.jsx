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
    <div className="fixture-page">
        <div className="title">
                Fixtures
        </div>

        <div className="all-fixtures">
                {allFixtures ? (
                    allFixtures.map(fixture => (
                        <FixtureList fixture={fixture} key={fixture._id} />
                    ))
                ):(
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