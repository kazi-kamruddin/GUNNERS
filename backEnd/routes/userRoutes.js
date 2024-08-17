const express = require('express');
const userModel = require('../models/userModel');
const {
    loginUser,
    signUpUser,
} = require('../controllers/userController');
const router = express.Router();

//login
router.post('/login', loginUser)

//signUp
router.post('/signUp', signUpUser)

module.exports = router;