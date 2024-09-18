const mongoose = require('mongoose');


const schema = mongoose.Schema;

const userInfoSchema = new schema({
    FirstName: {
        type: String,
        required: false,
    },
    LastName: {
        type: String,
        required: false,
    },
    DOB: {
        type: String,
        required: false,
    },
    Country: {
        type: String,
        required: false,
    }
}, { timestamps: true });

//static method
//cant use arrow func for this, cause 'this' is used inside





module.exports = mongoose.model('UserInfo', userInfoSchema);