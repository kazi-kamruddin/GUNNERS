import React, { useState,useEffect } from 'react';
import '../allCss/adminDashboard.css'; 
import { useAuthContext } from "../hook/useAuthContext";
import { useNavigate } from 'react-router-dom';

const AdminDashboard = () => {

    const { user } = useAuthContext();
    const navigate = useNavigate();

    const addNews =() => {
        console.log("navigate to addNews");
        navigate('/adminDashboard/addNews');
    }
    const editShop =() => {
        console.log("item added");
        navigate('/adminDashboard/editShop');
    }
    const editPlayers =() => {
        console.log("players added");
        navigate('/adminDashboard/editPlayers');
    }

    return (
        <div className="dashboard">
            <p>hail {user.email}</p>
            <p>it's the ADMIN dashboard</p>
            <button onClick={addNews}>
                add news
            </button>
            <button onClick={editShop}>
                edit shop
            </button>
            <button onClick={editPlayers}>
                edit Player list
            </button>
        </div>
    );
};

export default AdminDashboard;