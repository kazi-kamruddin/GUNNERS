const express = require('express');
const newsModel = require('../models/newsModel');
const {
    getAllNews,
    createNews,
    getSingleNews,
    deleteSingleNews,
    updateNews
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

router.delete('/editNews/:id', deleteSingleNews);

router.patch('/editNews/:id', updateNews);

module.exports = router;