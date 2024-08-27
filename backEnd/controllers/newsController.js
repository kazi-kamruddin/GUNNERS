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
    
    const {title, body, mainBody, imageLink} = req.body;
    try{
        const news = await newsModel.create({title, body, mainBody, imageLink});
        
        res.status(200).json(news);
    }
    catch (error){
        res.status(400).json({error : error.message});
    }
}

//delete a news
const deleteSingleNews = async (req,res) => {
    const {id} = req.params;
    if(!mongoose.Types.ObjectId.isValid(id))             
        return res.status(400).json({error : "no such news"});

    try{
        const deleteNews = await newsModel.findOneAndDelete({_id : id});
        if(!deleteNews)
            return res.status(400).json({error : "no such news"});

        res.status(200).json(deleteNews);
    }
    catch (error){
        res.status(400).json({error : error.message});
    }
}

//updat a news
const updateNews = async (req,res) => {
    const {id} = req.params;
    if(!mongoose.Types.ObjectId.isValid(id))           
        return res.status(400).json({error : "no such news"});

    try{
        const patchNews = await newsModel.findOneAndUpdate({_id : id}, {
            ...req.body                //destructuring the request body to edit fields
        });
        if(!patchNews)
            return res.status(400).json({error : "no such news"});

        res.status(200).json(patchNews);
    }
    catch (error){
        res.status(400).json({error : error.message});
    }
}


module.exports = {
    getAllNews,
    createNews,
    getSingleNews,
    deleteSingleNews,
    updateNews,
}