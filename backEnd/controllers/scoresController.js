const { default: mongoose } = require('mongoose');
const scoresModel = require('../models/scoresModel');

//create a new score
const createScore = async (req,res) => {
    console.log(req.body);
    
    const { date,competition,team1,team1Logo,team1Score,team1Scorers,team2,team2Logo,team2Score,team2Scorers,venue } = req.body;

    
    try{
        const scores = await scoresModel.create({date,competition,team1,team1Logo,team1Score,team1Scorers,team2,team2Logo,team2Score,team2Scorers,venue});
        res.status(200).json(scores);
    }
    catch (error){
        res.status(400).json({error : error.message});
    }
}

//get all scores
const getAllScores = async (req,res) => {
    try{
        const scores = await scoresModel.find({}).sort({createdAt: -1});
        res.status(200).json(scores);
    }
    catch (error){
        res.status(400).json({error : error.message});
    }
}

module.exports = {
    createScore,
    getAllScores,
}