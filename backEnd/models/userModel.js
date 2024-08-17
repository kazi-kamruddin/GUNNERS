const mongoose = require('mongoose');
const bcrypt = require('bcrypt');
const validator = require('validator');

const schema = mongoose.Schema;

const userSchema = new schema({
    email: {
        type: String,
        required: true,
        unique: true,
    },

    password: {
        type: String,
        required: true,
    }
})

//static method
//cant use arrow func for this, cause 'this' is used inside

userSchema.statics.login = async function (email, password) {

    //validation
    if(!email || !password){
        throw Error('need em both');
    }
    
    const currentUser = await this.findOne({ email });

    if(!currentUser){
        throw Error('incorrect email');
    }

    const match = await bcrypt.compare(password, currentUser.password);

    if(!match){
        throw Error('incorrect email');
    }

    return currentUser;
}

userSchema.statics.signUp = async function (email, password) {

    //validation
    if(!email || !password){
        throw Error('need em both');
    }
    if(!validator.isEmail(email)){
        throw Error('invalid email');
    }
    if(!validator.isStrongPassword(password)){
        throw Error('weak password');
    }

    const exists = await this.findOne({ email });

    if(exists){
        throw Error('email already in use');
    }

    const salt = await bcrypt.genSalt(8);
    const hash = await bcrypt.hash(password, salt);

    const user = await this.create({email, password: hash});

    return user; 
}

module.exports = mongoose.model('User', userSchema);