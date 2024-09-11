import React, { useState, useEffect } from 'react';
import '../allCss/adminDashboard.css'; 
import { useAuthContext } from "../hook/useAuthContext";
import { useNavigate } from 'react-router-dom';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, LineElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend } from 'chart.js';
ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend);

const AdminDashboard = () => {
    const { user } = useAuthContext();
    const navigate = useNavigate();
    const [userData, setUserData] = useState([0, 0, 0, 0, 0, 0, 0]);
    const [labels, setLabels] = useState([]);

    useEffect(() => {
        const getLast7Days = () => {
            const days = [];
            const today = new Date();
            
            for (let i = 6; i >= 0; i--) {
                const day = new Date(today);
                day.setDate(today.getDate() - i);
                days.push(day.toLocaleDateString('en-US', { weekday: 'long' })); 
            }
            return days;
        };

        const fetchUserCount = async () => {
            try {
                const response = await fetch('http://localhost:4000/api/adminDashboard');
                const data = await response.json();
        
                console.log('Fetched Data:', data); 
        
                const userCountsByDay = new Array(7).fill(0); 
                const last7Days = getLast7Days(); 
        
                const dataMap = data.reduce((map, dayData) => {
                    map[dayData._id] = dayData.count;
                    return map;
                }, {});
        
                last7Days.forEach((label, index) => {
                    const date = new Date();
                    date.setDate(date.getDate() - (6 - index));
                    const dateString = date.toISOString().split('T')[0];
                    userCountsByDay[index] = dataMap[dateString] || 0;
                });
        
                setUserData(userCountsByDay);
                setLabels(last7Days);
            } catch (error) {
                console.error('Error fetching user count:', error);
            }
        };

        fetchUserCount();
    }, []);

    const data = {
        labels: labels,
        datasets: [
            {
                label: 'User Count',
                color: 'rgba(230, 222, 222, 0.833)',
                data: userData, 
                borderColor: 'rgba(201, 0, 0, 0.904)', 
                backgroundColor: 'rgba(75, 192, 192, 0.2)', 
                borderWidth: 2, 
                pointBackgroundColor: 'rgba(201, 0, 0, 0.904)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(201, 0, 0, 0.904)',
                tension: 0.33, 
                fill: true, 
            },
        ],
    };
    
    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
                position: 'top',
                labels: {
                    font: {
                        size: 16,
                        weight: 'bold',
                    },
                    color: '#333',
                },
            },
            tooltip: {
                enabled: true,
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                titleFont: {
                    size: 16,
                    weight: 'bold',
                },
                bodyFont: {
                    size: 14,
                },
                footerFont: {
                    size: 12,
                    style: 'italic',
                },
                padding: 10, 
                caretSize: 6, 
            },
        },
        scales: {
            x: {
                title: {
                    display: true,
                    text: 'Days of the Week',
                    font: {
                        size: 16,
                        weight: 'bold',
                    },
                    color: 'rgba(230, 222, 222, 0.833)',
                },
                grid: {
                    display: false,
                },
                ticks: {
                    color: 'rgba(230, 222, 222, 0.833)',
                    font: {
                        size: 14,
                    },
                },
            },
            y: {
                title: {
                    display: true,
                    text: 'Number of Users',
                    font: {
                        size: 16,
                        weight: 'bold',
                    },
                    color: 'rgba(230, 222, 222, 0.833)',
                },
                beginAtZero: true,
                grid: {
                    borderColor: '#e0e0e0', 
                    borderWidth: 1,
                    color: 'rgba(0, 0, 0, 0.1)', 
                },
                ticks: {
                    stepSize: 1,
                    color: 'rgba(230, 222, 222, 0.833)',
                    font: {
                        size: 14,
                    },
                },
            },
        },
        animation: {
            duration: 1000, 
            easing: 'easeOutQuart', 
        },
    };
    
    

    const editNews =() => {
        console.log("navigate to addNews");
        navigate('/adminDashboard/editNews');
    }
    const editFixture =() => {
        console.log("navigate to edit Fixture");
        navigate('/adminDashboard/editFixture');
    }
    const editShop =() => {
        console.log("item added");
        navigate('/adminDashboard/editShop');
    }
    const editScores =() => {
        console.log("to edit scores page");
        navigate('/adminDashboard/editScores');
    }

    return (
        <div className="admin-dashboard-page">
            <div className="edit-options">
                <button onClick={editNews} className="edit-buttons"><text className='button-text'>EDIT NEWS</text></button>
                <button onClick={editFixture} className="edit-buttons"><text className='button-text'>EDIT FIXTURES</text></button>
                <button onClick={editShop} className="edit-buttons"><text className='button-text'>EDIT SHOP</text></button>
                <button onClick={editScores} className="edit-buttons"><text className='button-text'>EDIT SCORES</text></button>
            </div>

            <div className="chart-section">
                <div className="chart-background">
                    <div className="line-chart">
                        <Line data={data} options={options} />
                    </div>
                </div>

                <div className="chart-background">
                    <div className="line-chart">
                        <Line data={data} options={options} />
                    </div>
                </div>
            </div>
            
            
        </div>
    );
};

export default AdminDashboard;