import React, { useEffect, useState } from 'react';
import '../allCss/newsPage.css';
import NewsDetails from "../components/newsDetails.jsx";
import NewsNavBar from "../components/NewsNavBar.jsx";

const YouthNewsPage = () => {
    const [youthNews, setYouthNews] = useState([]);

    useEffect(() => {
        const fetchNews = async () => {
            const response = await fetch('http://localhost:4000/api/news');
            const json = await response.json();

            if (response.ok) {
    
                const filteredNews = json.filter(news => news.news_tag && news.news_tag.toLowerCase() === 'youth');
                setYouthNews(filteredNews);
            }
        }

        fetchNews();
    }, []);

    return (
        <div className="newsPage">
            <NewsNavBar />
            <div className="pageTitle">A C A D E M Y</div>
            <div className="news-grid">
                {youthNews.length > 0 ? (
                    youthNews.map(news => <NewsDetails news={news} key={news._id} />)
                ) : (
                    <p>No news available for Youth.</p>
                )}
            </div>
            <br /> <br />
        </div>
    );
};

export default YouthNewsPage;
