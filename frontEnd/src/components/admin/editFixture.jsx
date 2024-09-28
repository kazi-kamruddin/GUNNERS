import React, { useState, useEffect } from 'react';
import '../../allCss/editFixture.css';
import { useAuthContext } from "../../hook/useAuthContext";

const EditFixture = () => {
    const { user } = useAuthContext();
    const [date, setDate] = useState('');
    const [competition, setCompetition] = useState('');
    const [team1, setTeam1] = useState('');
    const [team2, setTeam2] = useState('');
    const [venue, setVenue] = useState('');
    const [form, setForm] = useState('');
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const [allFixture, setFixture] = useState(null);
    const [deleteTargetId, setDeleteTargetId] = useState(null);

    const clickedAddFixture = async (e) => {
        e.preventDefault();

        const fixtureData = { date, competition, team1, team2, venue, form };

        const response = await fetch('http://localhost:4000/api/adminDashboard/editFixture', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${user.token}`,
            },
            body: JSON.stringify(fixtureData),
        });

        const json = await response.json();

        if (!response.ok) {
            setError(json.error);
            setSuccess(null);
        } 
        else {
            setDate('');
            setCompetition('');
            setTeam1('');
            setTeam2('');
            setVenue('');
            setForm('');
            setError(null);
            setSuccess('fixture added successfully!');
        }
    };

    const clickedYesToDelete = async (fixture) => {
        console.log("delete him", fixture._id);
    
        const endpoint = `http://localhost:4000/api/adminDashboard/editFixture/${fixture._id}`;
        console.log(endpoint);
    
        try {
            const response = await fetch(endpoint, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${user.token}`,
                },
            });
    
            const json = await response.json();
    
            if (!response.ok) {
                setError(json.error);
                setSuccess(null);
            } else {
                setError(null);
                setSuccess('fixture deleted successfully!');
                setFixture((prevFixture) => prevFixture.filter(item => item._id !== fixture._id)); 
            }
        } catch (error) {
            console.error("Error deleting the fixture:", error);
            setError('Failed to delete the fixture. Please try again.');
        }
    };

    // fetches all the fixture, ttriggers when state of 'success' changes
    useEffect(() => {
        const fetchFixture = async () => {
            try {
                const response = await fetch('http://localhost:4000/api/fixture');
                if (!response.ok) {
                    throw new Error('Failed to fetch news');
                }
                const json = await response.json();
                setFixture(json);
            } catch (error) {
                console.error(error);
                setError('Could not load news. Please try again later.');
            }
        };
        fetchFixture();
    }, [success]);

    const handleDeleteClick = (fixture) => {
        setDeleteTargetId(fixture._id);
        console.log("target for deletion: ", fixture._id);
    };

    const handleCancelDelete = (fixture) => {
        setDeleteTargetId(null);
        console.log("clicked no", fixture._id);
    };

    const handleConfirmDelete = (fixture) => {
        setDeleteTargetId(null);
        clickedYesToDelete(fixture);
        console.log("clicked yes", fixture._id);
    };

    return (
        <div className="admin-edit-fixture">

            <form onSubmit={clickedAddFixture} className='edit-fixture-form'>
                <div className='edit-fixture-form-date'>
                    <label>Date:</label>
                    <input type="date" value={date} onChange={(e) => setDate(e.target.value)} required />
                </div>

                <div className='edit-fixture-form-competition'>
                    <label>Competition:</label>
                    <input type="text" value={competition} onChange={(e) => setCompetition(e.target.value)} required />
                </div>

                <div className='edit-fixture-form-team1'>
                    <label>Team 1:</label>
                    <input type="text" value={team1} onChange={(e) => setTeam1(e.target.value)} required />
                </div>

                <div className='edit-fixture-form-team2'>
                    <label>Team 2:</label>
                    <input type="text" value={team2} onChange={(e) => setTeam2(e.target.value)} required />
                </div>

                <div className='edit-fixture-form-venue'>
                    <label>Venue:</label>
                    <input type="text" value={venue} onChange={(e) => setVenue(e.target.value)} required />
                </div>

                <div className='edit-fixture-form-recent-form'>
                    <label>Form:</label>
                    <input type="text" value={form} onChange={(e) => setForm(e.target.value)} required />
                </div>

                <button type="submit"  className='edit-fixture-form-submit'>Add Fixture</button>
            </form>

            {error && <p className='status-messages'>{error}</p>}
            {success && <p className='status-messages'>{success}</p>}

            <div className="edit-fixture-all-fixtures">
                {allFixture && allFixture.map(fixture => (
                    <div className="edit-fixture-card" key={fixture._id}>
                        <div className="edit-fixture-card-header-date">{new Date(fixture.date).toLocaleDateString()}</div>
                        <div className="edit-fixture-card-header">
                            <div className="edit-fixture-card-header-team1">{fixture.team1}</div>
                            <div className="edit-fixture-card-header-versus">VS</div>
                            <div className="edit-fixture-card-header-team2">{fixture.team2}</div>
                        </div>

                        <button className="edit-fixture-card-delete-button" onClick={() => handleDeleteClick(fixture)}>
                            delete this fixture &#8594;
                        </button>

                        {deleteTargetId === fixture._id && (
                            <div className="confirmDeleteButtons">
                                <button onClick={() => handleConfirmDelete(fixture)} className="edit-fixture-card-delete-confirm">yes</button>
                                <button onClick={() => handleCancelDelete(fixture)} className="edit-fixture-card-delete-decline">no</button>
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default EditFixture;
