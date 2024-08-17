const mongoose = require('mongoose');

const schema = mongoose.Schema;

//document model for database
const newsSchema = new schema({
    title: {
        type: String,
        required: true,
    },

    body: {
        type: String,
        required: true,
    },

    mainBody: {
        type: String,
        required: true,
    },

    imageLink: {
        type: String,
        required: true,
    }
}, {timestamps: true})

module.exports = mongoose.model('News', newsSchema);