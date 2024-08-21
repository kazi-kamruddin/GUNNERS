const express = require('express');
const newsModel = require('../models/newsModel');
const {
    getAllNews,
    createNews,
    getSingleNews,
} = require('../controllers/newsController');
const router = express.Router();

// //all news
// router.get('/', getAllNews)

// //single news
// router.get('/:id', getSingleNews)

// //add a news
// router.post('/', createNews)

// //add a news
router.post('/addNews', createNews)

module.exports = router;