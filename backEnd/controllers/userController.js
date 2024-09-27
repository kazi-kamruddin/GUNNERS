const { default: mongoose } = require('mongoose');
const jwt = require('jsonwebtoken');
const userModel = require('../models/userModel');
const adminEmail = process.env.ADMIN_EMAIL;

const generateToken = (_id, role) => {
    //header, payload, signature
    //payload, secret sauce, token options 
    return jwt.sign({_id, role}, process.env.SECRET, {expiresIn:'2d'});
}

const loginUser = async (req, res) => {
    const { email, password } = req.body;

    try {
        const user = await userModel.login(email, password);
        const role = (email === adminEmail) ? 'admin' : 'regular';

        const token = generateToken(user._id, role);
        res.status(200).json({ email, token, user, role, message: "You're logged in" });
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
};

const signUpUser = async (req, res) => {
    const { email, password } = req.body;

    try {
        const user = await userModel.signUp(email, password);
        const role = (email === adminEmail) ? 'admin' : 'regular';

        const token = generateToken(user._id, role);
        res.status(200).json({ email, token, user, role, message: "You're signed up" });
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
};



module.exports = {
    loginUser,
    signUpUser,
}