const express = require('express');
const newsModel = require('../models/newsModel');
const {
    getAllNews,
    createNews,
} = require('../controllers/newsController');
const router = express.Router();

//all workout
router.get('/', getAllNews)

//add a workout
router.post('/', createNews)

module.exports = router;