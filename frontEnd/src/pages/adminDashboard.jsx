import React, { useState,useEffect } from 'react';
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

    useEffect(() => {
        const fetchUserCount = async () => {
            try {
                const response = await fetch('http://localhost:4000/api/adminDashboard');
                const data = await response.json();

                const userCountsByDay = new Array(7).fill(0); 
                
                data.forEach(dayData => {
                    userCountsByDay[dayData._id - 1] = dayData.count; 
                });

                setUserData(userCountsByDay);
            } catch (error) {
                console.error('Error fetching user count:', error);
            }
        };

        fetchUserCount();
    }, []);

    const data = {
        labels: ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
        datasets: [
            {
                label: 'User Count',
                data: userData, 
                borderColor: 'rgba(75,192,192,1)',
                backgroundColor: 'rgba(75,192,192,0.2)',
                borderWidth: 1,
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
            },
            tooltip: {
                enabled: true,
            },
        },
        scales: {
            x: {
                title: {
                    display: true,
                    text: 'Days of the Week',
                },
            },
            y: {
                title: {
                    display: true,
                    text: 'Number of Users',
                },
                beginAtZero: true,
                ticks: {
                    stepSize: 1, 
                },
            },
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
                <button onClick={editNews} className="edit-buttons">edit news</button>
                <button onClick={editFixture} className="edit-buttons">edit Fixture</button>
                <button onClick={editShop} className="edit-buttons">edit shop</button>
                <button onClick={editScores} className="edit-buttons">edit scores</button>
            </div>
            
            <div className="chart-area">
                <div className="line-chart">
                    <Line data={data} options={options} />
                </div>
            </div>
        </div>
    );
};

export default AdminDashboard;