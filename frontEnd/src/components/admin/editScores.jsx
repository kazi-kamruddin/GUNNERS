import React, { useState, useEffect } from 'react';
import '../../allCss/editScores.css';
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
            <form onSubmit={clickedAddScore} className='edit-score-form'>
            <div className='edit-score-form-date'>
                    <label>Date:</label>
                    <input type="date" value={date} onChange={(e) => setDate(e.target.value)} required />
                </div>

                <div className='edit-score-form-competition'>
                    <label>Competition:</label>
                    <input type="text" value={competition} onChange={(e) => setCompetition(e.target.value)} required />
                </div>

                <div className='edit-score-form-team1'>
                    <label>Team 1:</label>
                    <input type="text" value={team1} onChange={(e) => setTeam1(e.target.value)} required />
                </div>

                <div className='edit-score-form-team1-score'>
                    <label>Team 1 Score:</label>
                    <input type="number" value={team1Score} onChange={(e) => setTeam1Score(e.target.value)} required />
                </div>

                <div className='edit-score-form-team1-scorers'>
                    <label>Team 1 Scorers:</label>
                    <input
                        type="text"
                        value={team1Scorers.join('-')}
                        onChange={(e) => setTeam1Scorers(e.target.value.split('-').map(name => name.trim()))}
                        required
                    />
                    <small>Separate names with hyphens</small>
                </div>

                <div className='edit-score-form-team2'>
                    <label>Team 2:</label>
                    <input type="text" value={team2} onChange={(e) => setTeam2(e.target.value)} required />
                </div>

                <div className='edit-score-form-team2-score'>
                    <label>Team 2 Score:</label>
                    <input type="number" value={team2Score} onChange={(e) => setTeam2Score(e.target.value)} required />
                </div>

                <div className='edit-score-form-team2-scorers'>
                    <label>Team 2 Scorers:</label>
                    <input
                        type="text"
                        value={team2Scorers.join('-')}
                        onChange={(e) => setTeam2Scorers(e.target.value.split('-').map(name => name.trim()))}
                        required
                    />
                    <small>Separate names with hyphens</small>
                </div>

                <div className='edit-score-form-venue'>
                    <label>Venue:</label>
                    <input type="text" value={venue} onChange={(e) => setVenue(e.target.value)} required />
                </div>

                <button type="submit"  className='edit-score-form-button'>Add score</button>
            </form>

            {error && <p className='status-messages'>{error}</p>}
            {success && <p className='status-messages'>{success}</p>}

            <div className="edit-score-all-scores">
                {allScores && allScores.map(score => (
                    <div className="edit-score-card" key={score._id}>
                        <div className="edit-score-card-header-date">{new Date(score.date).toLocaleDateString()}</div>
                        <div className="edit-score-card-header">
                            <div className="edit-score-card-header-team1">{score.team1}</div>
                            <div className="edit-score-card-header-team1">{score.team1Score}</div>
                            <div className="edit-score-card-header-hyphen"> - </div>
                            <div className="edit-score-card-header-team1">{score.team2Score}</div>
                            <div className="edit-score-card-header-team2">{score.team2}</div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default EditScores;
