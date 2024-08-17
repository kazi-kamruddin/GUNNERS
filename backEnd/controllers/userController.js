const { default: mongoose } = require('mongoose');
const userModel = require('../models/userModel');

const loginUser = async (req,res) => {
    try{
        res.status(200).json({message: "logging in"});
    }
    catch (error){
        res.status(400).json({error : error.message});
    }
}

const signUpUser = async (req,res) => {
    const {email,password} = req.body;
    
    try{
        const user = await userModel.signUp(email,password);
        res.status(200).json({email,user});
    }
    catch (error){
        res.status(400).json({error : error.message});
    }
}


module.exports = {
    loginUser,
    signUpUser,
}