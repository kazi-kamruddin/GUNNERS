import React, { useState,useEffect } from 'react';
import { useAuthContext } from "../../hook/useAuthContext";

const EditFixture = () => {

    const { user } = useAuthContext();

    return (
        <div className="editFixture">
            <p>hail {user.email}</p>
            <p>edit editFixture</p>
        </div>
    );
};

export default EditFixture;