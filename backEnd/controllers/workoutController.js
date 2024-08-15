const { default: mongoose } = require('mongoose');
const workoutModel = require('../models/workoutModel');

//get all workouts
const getAllWorkouts = async (req,res) => {
    try{
        const allWorkouts = await workoutModel.find({}).sort({createdAt: -1});
        res.status(200).json(allWorkouts);
    }
    catch (error){
        res.status(400).json({error : error.message});
    }
}

//get a single workout
const getSingleWorkout = async (req,res) => {

        const {id} = req.params;
        if(!mongoose.Types.ObjectId.isValid(id))             //id ta valid kina check
            return res.status(400).json({error : "no such workout"});

        const singleWorkout = await workoutModel.findById(id);  
        if(!singleWorkout)
            return res.status(400).json({error : "no such workout"});

        res.status(200).json(singleWorkout);
}

//create a new workout
const createWorkout = async (req,res) => {
    console.log(req.body);
    
    const {title, load, reps} = req.body;
    try{
        const workout = await workoutModel.create({title, load, reps});
        res.status(200).json(workout);
    }
    catch (error){
        res.status(400).json({error : error.message});
    }
}

//delete a workout
const deleteOneWorkout = async (req,res) => {
    const {id} = req.params;
    if(!mongoose.Types.ObjectId.isValid(id))             //id ta valid kina check
        return res.status(400).json({error : "no such workout"});

    try{
        const deleteWorkout = await workoutModel.findOneAndDelete({_id : id});
        if(!deleteWorkout)
            return res.status(400).json({error : "no such workout"});

        res.status(200).json(deleteWorkout);
    }
    catch (error){
        res.status(400).json({error : error.message});
    }
}

//updat a workout
const updateWorkout = async (req,res) => {
    const {id} = req.params;
    if(!mongoose.Types.ObjectId.isValid(id))             //id ta valid kina check
        return res.status(400).json({error : "no such workout"});

    try{
        const patchWorkout = await workoutModel.findOneAndUpdate({_id : id}, {
            ...req.body                //destructuring the request body to edit fields
        });
        if(!patchWorkout)
            return res.status(400).json({error : "no such workout"});

        res.status(200).json(patchWorkout);
    }
    catch (error){
        res.status(400).json({error : error.message});
    }
}


module.exports = {
    createWorkout,
    getAllWorkouts,
    getSingleWorkout,
    deleteOneWorkout,
    updateWorkout
}