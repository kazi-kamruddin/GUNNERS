import React, { useState } from 'react';
import '../../allCss/editSingleNews.css';
import { useLocation, useNavigate } from "react-router-dom";

const EditSingleNews = () => {
    const location = useLocation();
    const news = location.state?.news;
    
    const initialTitle = news.title;
    const initialBody = news.body;
    const initialMainBody = news.mainBody;
    const initialImageLink = news.imageLink;

    const [title, setTitle] = useState(initialTitle);
    const [body, setBody] = useState(initialBody);
    const [mainBody, setMainBody] = useState(initialMainBody);
    const [imageLink, setImageLink] = useState(initialImageLink);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);

    const navigate = useNavigate();

    console.log("update this", news._id);
    
    const endpoint = `http://localhost:4000/api/adminDashboard/editNews/${news._id}`;
    console.log(endpoint);

    const clickedFinalizeEdit = async (e) => {
        e.preventDefault();

        if (title === initialTitle && body === initialBody && mainBody === initialMainBody && imageLink === initialImageLink) {
            setError("You haven't made any changes.");
            return;
        }

        const updatedNews = {
            title,
            body,
            mainBody,
            imageLink
        };

        try {
            const response = await fetch(endpoint, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${user.token}`,
                },
                body: JSON.stringify(updatedNews),
            });

            if (response.ok) {
                setSuccess("News updated successfully!");
                setError(null);
            } else {
                setError("Failed to update news.");
                setSuccess(null);
            }
        } catch (error) {
            setError("An error occurred: " + error.message);
            setSuccess(null);
        }
    };

    return (
        <div>
            <form onSubmit={clickedFinalizeEdit} className='edit-single-news-form'>
                <div className='edit-single-news-form-title'>
                    <label>Title:</label>
                    <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} required />
                </div>

                <div className='edit-single-news-form-body'>
                    <label>Body:</label>
                    <textarea value={body} onChange={(e) => setBody(e.target.value)} required />
                </div>

                <div className='edit-single-news-form-mainBody'>
                    <label>Main Body:</label>
                    <textarea value={mainBody} onChange={(e) => setMainBody(e.target.value)} required />
                </div>

                <div className='edit-single-news-form-imageLink'>
                    <label>Image Link:</label>
                    <input type="text" value={imageLink} onChange={(e) => setImageLink(e.target.value)} required />
                </div>

                <button type="submit"  className='edit-single-news-form-submit'>Edit News</button>
            </form>

            {error && <p  className='edit-single-news-error'>{error}</p>}
            {success && <p  className='edit-single-news-success'>{success}</p>} 

            <button onClick={() => window.history.back()} className="back-button">Back</button>
        </div>
    );
};

export default EditSingleNews;