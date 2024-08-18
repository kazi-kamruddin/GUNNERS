import { useState } from "react";
import { useAuthContext } from './useAuthContext';

export const useSignUp  = () => {
    const [error, setError] = useState(null);
    const [isLoading, setisLoading] = useState(null);
    const { dispatch } = useAuthContext();

    const signUp = async (email,password) => {
        setisLoading(true);
        setError(null);

        const response = await fetch('http://localhost:4000/api/user/signUp', {
            method : 'POST',
            headers : {'Content-Type' : 'application/json'},
            body : JSON.stringify({email,password}),
        })
        const json = await response.json();

        if(!response.ok){
            setisLoading(false);
            setError(json.error);
        }

        if(response.ok){
            //save current user in localStorage
            localStorage.setItem('user', JSON.stringify(json));

            //update auth context
            dispatch({type:'LOGIN', payload: json });

            setisLoading(false);
        }
    }

    return { signUp, isLoading, error }
}