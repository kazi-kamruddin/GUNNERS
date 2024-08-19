import React, { useState,useEffect } from 'react';
import '../allCss/dashboard.css'; 
import { useAuthContext } from "../hook/useAuthContext";

const FanPage = () => {

    const { user } = useAuthContext();

    return (
        <div className="dashboard">
            <p>Welcome {user.email}</p>
            <p>it's the dashboard</p>
        </div>
    );
};

export default FanPage;