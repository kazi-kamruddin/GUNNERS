const { default: mongoose } = require('mongoose');
const userModel = require('../models/userModel');
const jwt = require('jsonwebtoken');

const getUserCount = async (req, res) => {
    console.log("Authorization Header:", req.headers.authorization);
    try {
        const currentDate = new Date();
        const pastWeekDate = new Date();
        pastWeekDate.setDate(currentDate.getDate() - 6); 

        const formatDate = (date) => date.toISOString().split('T')[0];
        const formattedCurrentDate = formatDate(currentDate);
        const formattedPastWeekDate = formatDate(pastWeekDate);

        const userCount = await userModel.aggregate([
            {
                $match: {
                    createdAt: { $gte: new Date(formattedPastWeekDate), $lt: new Date(formattedCurrentDate + 'T23:59:59.999Z') }
                }
            },
            {
                $group: {
                    _id: { $dateToString: { format: "%Y-%m-%d", date: "$createdAt" } },
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