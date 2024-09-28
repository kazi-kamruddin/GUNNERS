import React, { useEffect, useState } from 'react';
import '../allCss/newsPage.css';
import NewsDetails from "../components/newsDetails.jsx";
import NewsNavBar from "../components/NewsNavBar.jsx";

const WomenNewsPage = () => {
    const [womenNews, setWomenNews] = useState([]);

    useEffect(() => {
        const fetchNews = async () => {
            const response = await fetch('http://localhost:4000/api/news');
            const json = await response.json();

            if (response.ok) {
                const filteredNews = json.filter(news => news.news_tag && news.news_tag.toLowerCase() === 'women');
                setWomenNews(filteredNews);
            }
        }

        fetchNews();
    }, []);

    return (
        <div className="newsPage">
            <NewsNavBar />
            <div className="pageTitle">W O M E N</div>
            <div className="news-grid">
                {womenNews.length > 0 ? (
                    womenNews.map(news => <NewsDetails news={news} key={news._id} />)
                ) : (
                    <p>No news available for Women.</p>
                )}
            </div>
            <br /> <br />
        </div>
    );
};

export default WomenNewsPage;
