import React, { useState,useEffect } from 'react';
import '../allCss/adminDashboard.css'; 
import { useAuthContext } from "../hook/useAuthContext";
import { useNavigate } from 'react-router-dom';

const AdminDashboard = () => {

    const { user } = useAuthContext();
    const navigate = useNavigate();

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
        <div className="dashboard">
            <p>hail {user.email}</p>
            <p>it's the ADMIN dashboard</p>
            <button onClick={editNews}>
                edit news
            </button>
            <button onClick={editFixture}>
                edit Fixture
            </button>
            <button onClick={editShop}>
                edit shop
            </button>
            <button onClick={editScores}>
                edit scores
            </button>
        </div>
    );
};

export default AdminDashboard;