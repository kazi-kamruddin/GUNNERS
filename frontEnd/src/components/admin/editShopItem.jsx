import React, { useState,useEffect } from 'react';
import { useAuthContext } from "../../hook/useAuthContext";

const editShopItem = () => {

    const { user } = useAuthContext();

    return (
        <div className="editShopItem">
            <p>hail {user.email}</p>
            <p>edit shop item</p>
        </div>
    );
};

export default editShopItem;