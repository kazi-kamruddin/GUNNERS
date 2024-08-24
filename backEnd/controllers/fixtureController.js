const { default: mongoose } = require('mongoose');
const newsModel = require('../models/fixtureModel');
const fixtureModel = require('../models/fixtureModel');

//create a new fixtrue
const createFixture = async (req,res) => {
    console.log(req.body);
    
    const {date,competition,team1,team1Logo,team2,team2Logo,venue,form} = req.body;
    
    try{
        const fixture = await fixtureModel.create({date,competition,team1,team1Logo,team2,team2Logo,venue,form});
        res.status(200).json(fixture);
    }
    catch (error){
        res.status(400).json({error : error.message});
    }
}

//get all fixture
const getAllFixture = async (req,res) => {
    try{
        const fixtures = await fixtureModel.find({}).sort({createdAt: -1});
        res.status(200).json(fixtures);
    }
    catch (error){
        res.status(400).json({error : error.message});
    }
}

module.exports = {
    createFixture,
    getAllFixture,
}