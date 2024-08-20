require('dotenv').config()

const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const app = express();

//route khujte ami kon file e jabo
const newsRoutes = require('./routes/newsRoutes.js');
const userRoutes = require('./routes/userRoutes.js');
const adminRoutes = require('./routes/adminRoutes.js');

//middleware
app.use(cors({
    origin: 'http://localhost:5173'     
}));

//these will run for every request
app.use(express.json());     //protita request er access pailam

app.use((req,res,next) => {
    console.log(req.path, req.method);
    next();
})

//routes
// app.get('/', (req,res) => {
//     res.json({message: "server is ok"});  
// })
app.use('/api/news', newsRoutes);
app.use('/api/user', userRoutes);
app.use('/api/adminDashboard', adminRoutes);

//connect to mongo
mongoose.connect(process.env.DB_URI)
    .then(() => {
        //listen to request
        console.log("connceted to DB");
        app.listen(process.env.PORT, () => {
            console.log(`listening on port`, process.env.PORT);
        })
    })
    .catch((error) => {
        console.log(error);
    })

// //listen to request
// app.listen(process.env.PORT, () => {
//     console.log(`listening on port`, process.env.PORT);
// })