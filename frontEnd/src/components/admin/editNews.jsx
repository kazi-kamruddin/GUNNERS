import React, { useState, useEffect } from 'react';
import '../../allCss/editNews.css';
import { useNavigate } from "react-router-dom";
import { useAuthContext } from "../../hook/useAuthContext";

const EditNews = () => {
    const { user } = useAuthContext();
    const navigate = useNavigate();
    const [title, setTitle] = useState('');
    const [body, setBody] = useState('');
    const [mainBody, setMainBody] = useState('');
    const [imageLink, setImageLink] = useState('');
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const [allNews, setNews] = useState(null);
    const [deleteTargetId, setDeleteTargetId] = useState(null);

    // triggers when adding news
    const clickedAddNews = async (e) => {
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
        } 
        else {
            setTitle('');
            setBody('');
            setMainBody('');
            setImageLink('');
            setError(null);
            setSuccess('News added successfully!');
        }
    };

    // triggers when presses yes to delete a news
    const clickedYesToDelete = async (news) => {
        console.log("delete him", news._id);
    
        const endpoint = `http://localhost:4000/api/adminDashboard/editNews/${news._id}`;
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
                setSuccess('News deleted successfully!');
                setNews((prevNews) => prevNews.filter(item => item._id !== news._id)); 
            }
        } catch (error) {
            console.error("Error deleting the news:", error);
            setError('Failed to delete the news. Please try again.');
        }
    };

    // fetches all the news, ttriggers when state of 'success' changes
    useEffect(() => {
        const fetchNews = async () => {
            try {
                const response = await fetch('http://localhost:4000/api/news');
                if (!response.ok) {
                    throw new Error('Failed to fetch news');
                }
                const json = await response.json();
                setNews(json);
            } catch (error) {
                console.error(error);
                setError('Could not load news. Please try again later.');
            }
        };
        fetchNews();
    }, [success]);

    const handleDeleteClick = (news) => {
        setDeleteTargetId(news._id);
        console.log("target for deletion: ", news._id, news.title);
    };

    const handleCancelDelete = (news) => {
        setDeleteTargetId(null);
        console.log("clicked no", news._id, news.title);
    };

    const handleConfirmDelete = (news) => {
        setDeleteTargetId(null);
        clickedYesToDelete(news);
    };

    return (
        <div className="admin-edit-news">
            <form onSubmit={clickedAddNews} className='edit-news-form'>
                <div className='edit-news-form-title'>
                    <label>title:</label>
                    <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} required />
                </div>

                <div  className='edit-news-form-body'>
                    <label>body:</label>
                    <textarea value={body} onChange={(e) => setBody(e.target.value)} required />
                </div>

                <div className='edit-news-form-mainBody'>
                    <label>main body:</label>
                    <textarea value={mainBody} onChange={(e) => setMainBody(e.target.value)} required />
                </div>

                <div  className='edit-news-form-imageLink'>
                    <label>image link:</label>
                    <input type="text" value={imageLink} onChange={(e) => setImageLink(e.target.value)} required />
                </div>

                <button type="submit"  className='edit-news-form-submit-button'>add news</button>
            </form>

            
            {error && <p>{error}</p>}
            {success && <p>{success}</p>} 
            news delete/add korte gele success/error message eikhane show korbe.

            <div className="edit-news-all-news">
                {allNews && allNews.map(news => (
                    <div className="edit-news-card" key={news._id}>
                        <div className="edit-news-card-title">
                            <h2>{news.title}</h2>
                        </div>
                        <div className="edit-news-card-body">
                            <img src={news.imageLink} alt="News" className="image" />
                            <p className="edit-news-card-body-text">{news.body}</p>
                        </div>
                        <button className="edit-news-card-editButton" onClick={() => navigate(`/adminDashboard/editNews/${news._id}`, { state: { news } })}>
                            Edit &#8594;
                        </button>
                        <button className="edit-news-card-deleteButton" onClick={() => handleDeleteClick(news)}>
                            delete this article &#8594;
                        </button>

                        {deleteTargetId === news._id && (
                            <div className="edit-news-card-delete-confirmation">
                                <button onClick={() => handleConfirmDelete(news)} className="edit-news-confirm-delete">YES</button>
                                <button onClick={() => handleCancelDelete(news)} className="edit-news-decline-delete">NO</button>
                            </div>
                        )}

                        <div className="edit-news-card-footer">
                            <p className="edit-news-card-footer-date">{new Date(news.createdAt).toLocaleDateString()}</p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default EditNews;
