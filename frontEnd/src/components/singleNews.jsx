import React, { useEffect, useState } from 'react';
import '../allCss/singleNews.css';

const SingleNews = () => {
    const currentUrl = window.location.href; 
    const modifiedUrl = currentUrl.replace('5173', '4000/api');

    const [news, setNews] = useState(null);

    useEffect(() => {
        const fetchNews = async () => {
            const response = await fetch(modifiedUrl);
            const json = await response.json();

            console.log(json);
            setNews(json);
        };

        fetchNews();
    }, [modifiedUrl]);

    return (
        <div className="single-news-body">
        <div className="single-news-container"> 
            {news && <h1 className="single-news-title">{news.title}</h1>}
            {news && <img className="single-news-image" src={news.imageLink} alt="News" />}
            {news && <p className="single-news-body">{news.mainBody}</p>}
            {news && <h1 className="single-news-title">{news.news_tag}</h1>}
            <button onClick={() => window.history.back()} className="single-news-back-button">Back</button>
        </div>
        </div>
    );

};

export default SingleNews;
