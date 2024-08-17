import React, { useEffect, useState } from 'react';
import '../allCss/newsPage.css';

import NewsDetails from "../components/newsDetails.jsx"

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
            <div className="pageTitle">
                    NEWS
            </div>
            <div className="allNews">
                {allNews && allNews.map(news => (
                    <NewsDetails news={news} key={news._id} />
                ))}
            </div>
        </div>
    )
};

export default NewsPage;
