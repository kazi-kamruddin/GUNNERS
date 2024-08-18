const { default: mongoose } = require('mongoose');
const jwt = require('jsonwebtoken');
const userModel = require('../models/userModel');

//generateToken
const generateToken = (_id) => {
    //header, payload, signature
    //payload, secret sauce, token options 
    return jwt.sign({_id}, process.env.SECRET, {expiresIn:'2d'});
}

const loginUser = async (req,res) => {
    const {email,password} = req.body;
    
    try{
        const user = await userModel.login(email,password);

        //token creation
        const token = generateToken(user._id);

        res.status(200).json({email,token,user,message:"you're logged in"});
    }
    catch (error){
        res.status(400).json({error : error.message});
    }
}

const signUpUser = async (req,res) => {
    const {email,password} = req.body;
    
    try{
        const user = await userModel.signUp(email,password);

        //token creation
        const token = generateToken(user._id);

        res.status(200).json({email,token,user,message:"you're signed up"});
    }
    catch (error){
        res.status(400).json({error : error.message});
    }
}


module.exports = {
    loginUser,
    signUpUser,
}