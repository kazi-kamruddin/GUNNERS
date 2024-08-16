const { default: mongoose } = require('mongoose');
const newsModel = require('../models/newsModel');

//get all news
const getAllNews = async (req,res) => {
    try{
        const allNews = await newsModel.find({}).sort({createdAt: -1});
        res.status(200).json(allNews);
    }
    catch (error){
        res.status(400).json({error : error.message});
    }
}

//get a single news
const getSingleNews = async (req,res) => {

    const {id} = req.params;
    if(!mongoose.Types.ObjectId.isValid(id))           
        return res.status(400).json({error : "no such news"});

    const singleNews = await newsModel.findById(id);  
    if(!singleNews)
        return res.status(400).json({error : "no such news"});

    res.status(200).json(singleNews);
}

//create a new news
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
    getSingleNews,
}