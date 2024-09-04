import React from "react";
import '../allCss/fixtureList.css';

const FixtureList = ({ fixture }) => {

  return (
    <div className="single-fixture-card">
        <div className="single-fixture-info">
            <div className="info-header">
                eikhane date, competition.
            </div>
            <div className="info-body">
                <div className="gg">{fixture.form}</div>
                <div className="gg">{fixture.form}</div>
                <div className="gg">{fixture.form}</div>
                <div className="gg">{fixture.form}</div>
                <div className="gg">{fixture.form}</div>
            </div>
            <div className="info-footer">
                news button
            </div>
            
        </div>
        
        <div className="divider"></div>
    </div>
  );
};

export default FixtureList;
