const jwt = require('jsonwebtoken');

const requireAdmin = (req, res, next) => {
    const token = req.headers.authorization?.split(' ')[1];

    if (!token) {
        return res.status(401).json({ message: "No token provided" });
    }

    try {
        const decoded = jwt.verify(token, process.env.SECRET);
        
        if (decoded.role !== 'admin') {
            return res.status(403).json({ message: "Need admin previleges" });
        }

        req.user = decoded;
        next();
    } catch (error) {
        return res.status(401).json({ message: "Invalid or expired token" });
    }
};

module.exports = requireAdmin;
