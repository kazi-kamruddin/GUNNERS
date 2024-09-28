const express = require('express');
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
    deleteSingleFixture,
} = require('../controllers/fixtureController');

const {
    getAllScores,
    createScore,
} = require('../controllers/scoresController');

const {
    getUserCount
} = require('../controllers/adminController');

const requireAdmin = require('../middleware/checkAdmin');
const router = express.Router();   


//newsBlock
router.post('/addNews', createNews)
router.delete('/editNews/:id', deleteSingleNews);
router.patch('/editNews/:id', updateNews);

//fixtureBlock
router.post('/editFixture', createFixture)
router.get('/editFixture', getAllFixture)
router.delete('/editFixture/:id', deleteSingleFixture);

//scoreBlock
router.get('/editScores', getAllScores)
router.post('/editScores', createScore)

//chart-stuff
router.get('/', requireAdmin, getUserCount);


module.exports = router;