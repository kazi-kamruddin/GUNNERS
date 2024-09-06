const { default: mongoose } = require('mongoose');
const userModel = require('../models/userModel');


const getUserCount = async (req, res) => {
    try {
        const currentDate = new Date();
        const pastWeekDate = new Date();
        pastWeekDate.setDate(currentDate.getDate() - 7);

        const userCount = await userModel.aggregate([
            {
                $match: {
                    createdAt: { $gte: pastWeekDate, $lt: currentDate }  
                }
            },
            {
                $group: {
                    _id: { $dayOfWeek: "$createdAt" },
                    count: { $sum: 1 }
                }
            },
            {
                $sort: { _id: 1 }
            }
        ]);

        res.status(200).json(userCount);
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Error fetching user count' });
    }
};



module.exports = {
    getUserCount,
}