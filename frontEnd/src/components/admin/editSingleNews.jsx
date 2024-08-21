import React, { useState } from 'react';
import '../../allCss/editSingleNews.css';
import { useLocation, useNavigate } from "react-router-dom";

const EditSingleNews = () => {
    const location = useLocation();
    const news = location.state?.news;
    
    // Store the initial values
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
            <h1>Edit News</h1>
            <p>{news.title}</p>
            <p>{news.body}</p>
            <p>{news.mainBody}</p>

            <form onSubmit={clickedFinalizeEdit}>
                <div>
                    <label>Title:</label>
                    <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} required />
                </div>

                <div>
                    <label>Body:</label>
                    <textarea value={body} onChange={(e) => setBody(e.target.value)} required />
                </div>

                <div>
                    <label>Main Body:</label>
                    <textarea value={mainBody} onChange={(e) => setMainBody(e.target.value)} required />
                </div>

                <div>
                    <label>Image Link:</label>
                    <input type="text" value={imageLink} onChange={(e) => setImageLink(e.target.value)} required />
                </div>

                <button type="submit">Edit News</button>
            </form>

            {error && <p style={{ color: 'red' }}>{error}</p>}
            {success && <p style={{ color: 'green' }}>{success}</p>} 

            <button onClick={() => window.history.back()} className="back-button">Back</button>
        </div>
    );
};

export default EditSingleNews;

// import React, { useEffect, useState } from 'react';
// import '../../allCss/editSingleNews.css';
// import { useLocation,useNavigate } from "react-router-dom";

// const EditSingleNews = () => {
//     const location = useLocation();
//     const news = location.state?.news;
//     const [title, setTitle] = useState(news.title);
//     const [body, setBody] = useState(news.body);
//     const [mainBody, setMainBody] = useState(news.mainBody);
//     const [imageLink, setImageLink] = useState(news.imageLink);
//     const [error, setError] = useState(null);
//     const [success, setSuccess] = useState(null);

//     console.log("update this", news._id);
    
//     const endpoint = `http://localhost:4000/api/adminDashboard/editNews/${news._id}`;
//     console.log(endpoint);

//     const clickedFinalizeEdit = (e) => {
//         e.preventDefault();
//         console.log("gg");
//     }

//     return (
//         <div>
//             <h1>Edit News</h1>
//             <p>{news.title}</p>
//             <p>{news.body}</p>
//             <p>{news.mainBody}</p>

//             <form onSubmit={clickedFinalizeEdit}>
//                 <div>
//                     <label>title:</label>
//                     <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} required />
//                 </div>

//                 <div>
//                     <label>body:</label>
//                     <textarea value={body} onChange={(e) => setBody(e.target.value)} required />
//                 </div>

//                 <div>
//                     <label>main body:</label>
//                     <textarea value={mainBody} onChange={(e) => setMainBody(e.target.value)} required />
//                 </div>

//                 <div>
//                     <label>image link:</label>
//                     <input type="text" value={imageLink} onChange={(e) => setImageLink(e.target.value)} required />
//                 </div>

//                 <button type="submit">edit news</button>
//             </form>

            
//             {error && <p>{error}</p>}
//             {success && <p>{success}</p>} 


//             <button onClick={() => window.history.back()} className="back-button">Back</button>
//         </div>
//     );
// };


// export default EditSingleNews;
