const mongoose = require('mongoose');
const schema = mongoose.Schema;

const fixtureSchema = new schema({ 
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

    team2: {
        type: String,
        required: true,
    },
    venue: {
        type: String,
        required: true,
    },

    form: {
        type: String, 
        required: false,
    },
    
}, {timestamps: true})


module.exports = mongoose.model('fixture', fixtureSchema);