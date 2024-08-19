import React, { useState,useEffect } from 'react';
import '../allCss/adminDashboard.css'; 
import { useAuthContext } from "../hook/useAuthContext";

const AdminDashboard = () => {

    const { user } = useAuthContext();

    return (
        <div className="dashboard">
            <p>hail {user.email}</p>
            <p>it's the ADMIN dashboard</p>
        </div>
    );
};

export default AdminDashboard;