import React, { useEffect, useState } from 'react';
import '../../allCss/editSingleNews.css';
import { useLocation,useNavigate } from "react-router-dom";

const EditSingleNews = () => {
    const location = useLocation();
    const news = location.state?.news;

    console.log(news);

    return (
        <div>
            <h1>Edit News</h1>
            <p>{news.title}</p>
            <p>{news.body}</p>
            <p>{news.mainBody}</p>
        </div>
    );
};


// const EditNews = () => {
//     const currentUrl = window.location.href; 
//     const modifiedUrl = currentUrl.replace('5173', '4000/api');

//     const [news, setNews] = useState(null);

//     useEffect(() => {
//         const fetchNews = async () => {
//             const response = await fetch(modifiedUrl);
//             const json = await response.json();

//             console.log(json);
//             setNews(json);
//         };

//         fetchNews();
//     }, [modifiedUrl]);

//     return (
//         <div> 
//             {news && <p>{news.title}</p>}
//             {news && <p>{news.title}</p>}
//             {news && <img src={news.imageLink}/>}
//             {news && <p>{news.mainBody}</p>}
//             <button onClick={() => window.history.back()} className="back-button">Back</button>
//         </div>
//     );
// };

export default EditSingleNews;
