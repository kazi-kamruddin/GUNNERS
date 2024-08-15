const express = require('express');
const workoutModel = require('../models/workoutModel');
const {
    createWorkout,
    getAllWorkouts,
    getSingleWorkout,
    deleteOneWorkout,
    updateWorkout
} = require('../controllers/workoutController');
const router = express.Router();

//all workout
router.get('/', getAllWorkouts)

//specific workout
router.get('/:id', getSingleWorkout)

// //add a workout
// router.post('/', (req,res) => {
//     res.json({message: "added a workout"});
// })

//add a workout
router.post('/', createWorkout)

//delete a workout
router.delete('/:id', deleteOneWorkout)

//edited an workout
router.patch('/:id', updateWorkout)

module.exports = router;