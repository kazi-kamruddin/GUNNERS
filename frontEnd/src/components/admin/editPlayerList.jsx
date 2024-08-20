import React, { useState,useEffect } from 'react';
import { useAuthContext } from "../../hook/useAuthContext";

const editPlayerList = () => {

    const { user } = useAuthContext();

    return (
        <div className="editPlayerList">
            <p>hail {user.email}</p>
            <p>edit Player List</p>
        </div>
    );
};

export default editPlayerList;