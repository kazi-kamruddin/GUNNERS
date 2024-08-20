import React, { useState } from 'react';
import { useAuthContext } from "../../hook/useAuthContext";

const AddNews = () => {
    const { user } = useAuthContext();
    const [title, setTitle] = useState('');
    const [body, setBody] = useState('');
    const [mainBody, setMainBody] = useState('');
    const [imageLink, setImageLink] = useState('');
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();

        const newsData = { title, body, mainBody, imageLink };

        const response = await fetch('http://localhost:4000/api/adminDashboard/addNews', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${user.token}`,
            },
            body: JSON.stringify(newsData),
        });

        const json = await response.json(); 

        if (!response.ok) {
            setError(json.error);
            setSuccess(null);
        } else {
            setTitle('');
            setBody('');
            setMainBody('');
            setImageLink('');
            setError(null);
            setSuccess('News added successfully!');
        }
    };

    return (
        <div className="adminAddNews">
            <p>hail {user.email}</p>
            <p>add news page</p>

            <form onSubmit={handleSubmit}>
                <div>
                    <label>title:</label>
                    <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} required/>
                </div>

                <div>
                    <label>body:</label>
                    <textarea value={body} onChange={(e) => setBody(e.target.value)} required />
                </div>

                <div>
                    <label>main body:</label>
                    <textarea value={mainBody} onChange={(e) => setMainBody(e.target.value)} required/>
                </div>

                <div>
                    <label>image link:</label>
                    <input type="text" value={imageLink} onChange={(e) => setImageLink(e.target.value)} required />
                </div>

                <button type="submit">add news</button>
            </form>

            {error && <p>{error}</p>}
            {success && <p>{success}</p>}
        </div>
    );
};

export default AddNews;