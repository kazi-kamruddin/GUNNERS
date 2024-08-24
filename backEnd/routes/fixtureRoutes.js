const express = require('express');
const newsModel = require('../models/fixtureModel');
const {
    getAllFixture,
} = require('../controllers/fixtureController');
const router = express.Router();


router.get('/', getAllFixture)




module.exports = router;