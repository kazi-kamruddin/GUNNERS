const express = require('express');
const newsModel = require('../models/newsModel');
const {
    getAllNews,
    createNews,
    getSingleNews,
    deleteSingleNews,
    updateNews
} = require('../controllers/newsController');

const {
    createFixture,
    getAllFixture,
} = require('../controllers/fixtureController');
const router = express.Router();

//newsBlock
router.post('/addNews', createNews)
router.delete('/editNews/:id', deleteSingleNews);
router.patch('/editNews/:id', updateNews);

//fixtureBlock
router.post('/editFixture', createFixture)
router.get('/editFixture', getAllFixture)



module.exports = router;