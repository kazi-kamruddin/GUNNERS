import React, { useEffect, useState } from 'react';
import '../allCss/newsPage.css';
import NewsDetails from "../components/newsDetails.jsx";
import NewsNavBar from "../components/NewsNavBar.jsx"; // Import the new NewsNavBar

const NewsPage = () => {
    const [allNews, setNews] = useState(null)

    useEffect(() => {
        const fetchNews = async () => {
            const response = await fetch('http://localhost:4000/api/news');
            const json = await response.json();

            if (response.ok) {
                setNews(json)
            }
        }

        fetchNews()
    }, [])

    return (
        <div className="newsPage">
            <NewsNavBar /> 
            <div className="pageTitle">
                NEWS
            </div>
            <div className="news-grid">
                {allNews && allNews.map(news => (
                    <NewsDetails news={news} key={news._id}/>
                ))}
            </div>
        </div>
    )
};

export default NewsPage;
