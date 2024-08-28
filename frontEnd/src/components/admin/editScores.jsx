import React, { useState, useEffect } from 'react';
import '../../allCss/editFixture.css';
import { useAuthContext } from "../../hook/useAuthContext";

const EditScores = () => {
    const { user } = useAuthContext();
    const [date, setDate] = useState('');
    const [competition, setCompetition] = useState('');
    const [team1, setTeam1] = useState('');
    const [team1Logo, setTeam1Logo] = useState('');
    const [team1Score, setTeam1Score] = useState('');
    const [team1Scorers, setTeam1Scorers] = useState([]);
    const [team2, setTeam2] = useState('');
    const [team2Logo, setTeam2Logo] = useState('');
    const [team2Score, setTeam2Score] = useState('');
    const [team2Scorers, setTeam2Scorers] = useState([]);
    const [venue, setVenue] = useState('');
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const [allScores, setScore] = useState(null);

    const clickedAddScore = async (e) => {
        e.preventDefault();

        const scoreData = { date, competition, team1, team1Logo, team1Score, team1Scorers, team2, team2Logo, team2Score, team2Scorers, venue };

        const response = await fetch('http://localhost:4000/api/adminDashboard/editScores', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${user.token}`,
            },
            body: JSON.stringify(scoreData),
        });

        const json = await response.json();

        if (!response.ok) {
            setError(json.error);
            setSuccess(null);
        } else {
            setSuccess('Score added successfully!');
            setError(null);
            setDate('');
            setCompetition('');
            setTeam1('');
            setTeam1Logo('');
            setTeam1Score('');
            setTeam1Scorers([]);
            setTeam2('');
            setTeam2Logo('');
            setTeam2Score('');
            setTeam2Scorers([]);
            setVenue('');
        }
    };

    useEffect(() => {
        const fetchScores = async () => {
            try {
                const response = await fetch('http://localhost:4000/api/scores');
                if (!response.ok) {
                    throw new Error('Failed to fetch scores');
                }
                const json = await response.json();
                setScore(json);
            } catch (error) {
                console.error(error);
                setError('Could not load scores. Please try again later.');
            }
        };
        fetchScores();
    }, [success]);

    return (
        <div className="adminEditScores">
            <p>hail {user.email}</p>
            <p>edit scores page</p>

            <form onSubmit={clickedAddScore}>
                <div>
                    <label>Date:</label>
                    <input type="text" value={date} onChange={(e) => setDate(e.target.value)} required />
                </div>

                <div>
                    <label>Competition:</label>
                    <input type="text" value={competition} onChange={(e) => setCompetition(e.target.value)} required />
                </div>

                <div>
                    <label>Team 1:</label>
                    <input type="text" value={team1} onChange={(e) => setTeam1(e.target.value)} required />
                </div>

                <div>
                    <label>Team 1 Logo:</label>
                    <input type="text" value={team1Logo} onChange={(e) => setTeam1Logo(e.target.value)} required />
                </div>

                <div>
                    <label>Team 1 Score:</label>
                    <input type="number" value={team1Score} onChange={(e) => setTeam1Score(e.target.value)} required />
                </div>

                <div>
                    <label>Team 1 Scorers:</label>
                    <input
                        type="text"
                        value={team1Scorers.join('-')}
                        onChange={(e) => setTeam1Scorers(e.target.value.split('-').map(name => name.trim()))}
                        required
                    />
                    <small>Separate names with hyphens</small>
                </div>

                <div>
                    <label>Team 2:</label>
                    <input type="text" value={team2} onChange={(e) => setTeam2(e.target.value)} required />
                </div>

                <div>
                    <label>Team 2 Logo:</label>
                    <input type="text" value={team2Logo} onChange={(e) => setTeam2Logo(e.target.value)} required />
                </div>

                <div>
                    <label>Team 2 Score:</label>
                    <input type="number" value={team2Score} onChange={(e) => setTeam2Score(e.target.value)} required />
                </div>

                <div>
                    <label>Team 2 Scorers:</label>
                    <input
                        type="text"
                        value={team2Scorers.join('-')}
                        onChange={(e) => setTeam2Scorers(e.target.value.split('-').map(name => name.trim()))}
                        required
                    />
                    <small>Separate names with hyphens</small>
                </div>

                <div>
                    <label>Venue:</label>
                    <input type="text" value={venue} onChange={(e) => setVenue(e.target.value)} required />
                </div>

                <button type="submit">Add score</button>
            </form>

            {error && <p>{error}</p>}
            {success && <p>{success}</p>}

            <div className="allScores">
                {allScores && allScores.map(score => (
                    <div className="fixtureCard" key={score._id}>
                        <p>{score.date}</p>
                        <p>{score.competition}</p>
                        <div className="teamInfo">
                            <p>{score.team1}</p>
                            <img src={score.team1Logo} alt="team1" className="image1" />
                            <p>Score: {score.team1Score}</p>
                            <p>Scorers: {score.team1Scorers.join(', ')}</p>
                        </div>
                        <div className="teamInfo">
                            <p>{score.team2}</p>
                            <img src={score.team2Logo} alt="team2" className="image2" />
                            <p>Score: {score.team2Score}</p>
                            <p>Scorers: {score.team2Scorers.join(', ')}</p>
                        </div>
                        <p>{score.venue}</p>
                        <p>Form: {score.form}</p>
                        <div className="footer">
                            <p className="date">{new Date(score.createdAt).toLocaleDateString()}</p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default EditScores;
