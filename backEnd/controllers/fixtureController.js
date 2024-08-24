const { default: mongoose } = require('mongoose');
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

//delete a fixtuer
const deleteSingleFixture = async (req,res) => {
    const {id} = req.params;
    if(!mongoose.Types.ObjectId.isValid(id))             
        return res.status(400).json({error : "no such fixture"});

    try{
        const deleteFixture = await fixtureModel.findOneAndDelete({_id : id});
        if(!deleteFixture)
            return res.status(400).json({error : "no such fixture"});

        res.status(200).json(deleteFixture);
    }
    catch (error){
        res.status(400).json({error : error.message});
    }
}

module.exports = {
    createFixture,
    getAllFixture,
    deleteSingleFixture,
}