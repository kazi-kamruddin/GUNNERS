import { useEffect, useState } from 'react';

const useFetchNews = () => {
    const [allNews, setNews] = useState(null);

    useEffect(() => {
        const fetchNews = async () => {
            const response = await fetch('http://localhost:4000/api/news');
            const json = await response.json();

            if (response.ok) {
                setNews(json);
            }
        }

        fetchNews();
    }, []);

    return allNews;
}

export default useFetchNews;
