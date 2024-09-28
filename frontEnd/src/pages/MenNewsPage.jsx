import React, { useEffect, useState } from 'react';
import '../allCss/newsPage.css';
import NewsDetails from "../components/newsDetails.jsx";
import NewsNavBar from "../components/NewsNavBar.jsx";

const MenNewsPage = () => {
    const [menNews, setMenNews] = useState([]);

    useEffect(() => {
        const fetchNews = async () => {
            const response = await fetch('http://localhost:4000/api/news');
            const json = await response.json();

            if (response.ok) {
       
                const filteredNews = json.filter(news => news.news_tag && news.news_tag.toLowerCase() === 'men');
                setMenNews(filteredNews);
            }
        }

        fetchNews();
    }, []);

    return (
        <div className="newsPage">
            <NewsNavBar /> 
            <div className="pageTitle">M E N</div>
            <div className="news-grid">
                {menNews.length > 0 ? (
                    menNews.map(news => <NewsDetails news={news} key={news._id} />)
                ) : (
                    <p>No news available for Men.</p>
                )}
            </div>
            <br /> <br />
        </div>
       
    
    );
};

export default MenNewsPage;
