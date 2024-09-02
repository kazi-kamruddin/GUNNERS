const mongoose = require('mongoose');
const schema = mongoose.Schema;

const scoresSchema = new schema({
    date: {
        type: String,
        required: true,
    },

    competition: {
        type: String,
        required: true,
    },

    team1: {
        type: String,
        required: true,
    },

    team1Score: {
        type: String,
        required: true,
    },

    team1Scorers: {
        type: [String], 
        required: false,
    },

    team2: {
        type: String,
        required: true,
    },

    team2Score: {
        type: String,
        required: true,
    },

    team2Scorers: {
        type: [String], 
        required: false,
    },

    venue: {
        type: String,
        required: true,
    },
    
}, {timestamps: true})


module.exports = mongoose.model('Score', scoresSchema);