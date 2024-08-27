import React, { useState, useEffect } from 'react';
import '../../allCss/editFixture.css';
import { useAuthContext } from "../../hook/useAuthContext";

const EditFixture = () => {
    const { user } = useAuthContext();
    const [date, setDate] = useState('');
    const [competition, setCompetition] = useState('');
    const [team1, setTeam1] = useState('');
    const [team1Logo, setTeam1Logo] = useState('');
    const [team2, setTeam2] = useState('');
    const [team2Logo, setTeam2Logo] = useState('');
    const [venue, setVenue] = useState('');
    const [form, setForm] = useState('');
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const [allFixture, setFixture] = useState(null);
    const [deleteTargetId, setDeleteTargetId] = useState(null);

    // triggers when adding news
    const clickedAddFixture = async (e) => {
        e.preventDefault();

        const fixtureData = { date, competition, team1, team1Logo, team2, team2Logo, venue, form };

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
            setTeam1Logo('');
            setTeam2('');
            setTeam2Logo('');
            setVenue('');
            setForm('');
            setError(null);
            setSuccess('fixture added successfully!');
        }
    };

    //triggers when presses yes to delete a fixture
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
        <div className="adminEditFixture">
            <p>hail {user.email}</p>
            <p>edit Fixture page</p>

            <form onSubmit={clickedAddFixture}>
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
                    <label>Team 2:</label>
                    <input type="text" value={team2} onChange={(e) => setTeam2(e.target.value)} required />
                </div>

                <div>
                    <label>Team 2 Logo:</label>
                    <input type="text" value={team2Logo} onChange={(e) => setTeam2Logo(e.target.value)} required />
                </div>

                <div>
                    <label>Venue:</label>
                    <input type="text" value={venue} onChange={(e) => setVenue(e.target.value)} required />
                </div>

                <div>
                    <label>Form:</label>
                    <input type="text" value={form} onChange={(e) => setForm(e.target.value)} required />
                </div>

                <button type="submit">Add Fixture</button>
            </form>


            {error && <p>{error}</p>}
            {success && <p>{success}</p>} 
            fixture delete/add korte gele success/error message eikhane show korbe.

            <div className="allFixtures">
                {allFixture && allFixture.map(fixture => (
                    <div className="fixtureCard" key={fixture._id}>
                        <p>{fixture.date}</p>
                        <p>{fixture.competition}</p>
                        <p>{fixture.team1}</p>
                        <img src={fixture.team1Logo} alt="team1" className="image1" />
                        <p>{fixture.team2}</p>
                        <img src={fixture.team2Logo} alt="team2" className="image2" />
                        <p>{fixture.venue}</p>
                        <p>{fixture.form}</p>
                        <button className="deleteButton" onClick={() => handleDeleteClick(fixture)}>
                            delete this fixture &#8594;
                        </button>

                        {deleteTargetId === fixture._id && (
                            <div className="confirmDeleteButtons">
                                <button onClick={() => handleConfirmDelete(fixture)} className="yesButton">yes</button>
                                <button onClick={() => handleCancelDelete(fixture)} className="noButton">no</button>
                            </div>
                        )}

                        <div className="footer">
                            <p className="date">{new Date(fixture.createdAt).toLocaleDateString()}</p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default EditFixture;
