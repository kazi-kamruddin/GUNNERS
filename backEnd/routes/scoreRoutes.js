const express = require('express');
const scoresModel = require('../models/scoresModel');
const {
    getAllScores,
} = require('../controllers/scoresController');
const router = express.Router();


router.get('/', getAllScores)



module.exports = router;