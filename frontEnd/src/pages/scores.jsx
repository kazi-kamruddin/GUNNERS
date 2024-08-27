import React from "react";
import { useState, useEffect } from "react";
import ScoresList from '../components/scoresList';

const Scores = () => {
  
  const [allScores, setScore] = useState(null)

  useEffect(() => {
      const fetchScore = async () => {
          const response = await fetch('http://localhost:4000/api/scores');
          const json = await response.json();

          if (response.ok) {
              setScore(json)
          }
      }

      fetchScore()
  }, [])

  return (
    <div className="scoresPage">
        <div className="pageTitle">
            Scores
        </div>
        <div className="allScores">
            {allScores && allScores.map(score => (
                <ScoresList score={score} key={score._id} />
            ))}
        </div>
    </div>
  );
};

export default Scores;