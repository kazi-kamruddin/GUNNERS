const { default: mongoose } = require('mongoose');
const newsModel = require('../models/newsModel');

//get all workouts
const getAllNews = async (req,res) => {
    try{
        const allNews = await newsModel.find({}).sort({createdAt: -1});
        res.status(200).json(allNews);
    }
    catch (error){
        res.status(400).json({error : error.message});
    }
}

//create a new workout
const createNews = async (req,res) => {
    console.log(req.body);
    
    const {title, body, imageLink} = req.body;
    try{
        const news = await newsModel.create({title, body, imageLink});
        res.status(200).json(news);
    }
    catch (error){
        res.status(400).json({error : error.message});
    }
}


module.exports = {
    getAllNews,
    createNews,
}