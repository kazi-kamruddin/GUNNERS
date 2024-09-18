import React, { useState } from 'react';
import '../allCss/dashboard.css'; 
import { useAuthContext } from "../hook/useAuthContext";
import { useLogout } from "../hook/useLogout";

const FanPage = () => {
    const { logout } = useLogout();
    const { user } = useAuthContext(); // Assuming user context is already set up
    const [isEditing, setIsEditing] = useState(false);
    const [profileName, setProfileName] = useState({
        firstName: user?.firstName || '',
        lastName: user?.lastName || ''
    });

    const [formData, setFormData] = useState({
        firstName: user?.firstName || '',
        lastName: user?.lastName || '',
        dateOfBirth: user?.dateOfBirth || '',
        country: user?.country || ''
    });
    
    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData({
            ...formData,
            [name]: value
        });
    };

    const handleEditClick = () => {
        setIsEditing(true);
    };

    const handleFormSubmit = (e) => {
        e.preventDefault();
        // Simulating form submission and updating profileName
        setProfileName({
            firstName: formData.firstName,
            lastName: formData.lastName
        });
        setIsEditing(false); // Hide form after submission
    };

    const handleLogout = () => {
        logout(); // Call logout function from context or authentication service
    };

    return (
        <div className="dashboard">
            <p className="dashboard-title">MY PROFILE</p>
            {profileName.firstName || profileName.lastName ? (
                <p>{profileName.firstName} {profileName.lastName}</p>
            ) : (
                <p>No name available</p>
            )}
            {user ? (
                <>
                    

                    <p>Email: {user.email}</p>
                    {!isEditing ? (
                        <>
                            <button className="edit-button" onClick={handleEditClick}>Edit</button>
                            {/* <button className="logout-button" onClick={handleLogout}>Logout</button> */}
                        </>
                    ) : (
                        <form onSubmit={handleFormSubmit} className="edit-form">
                            <div className="form-group">
                                <label htmlFor="firstName">First Name:</label>
                                <input
                                    type="text"
                                    id="firstName"
                                    name="firstName"
                                    value={formData.firstName}
                                    onChange={handleInputChange}
                                    required
                                />
                            </div>
                            <div className="form-group">
                                <label htmlFor="lastName">Last Name:</label>
                                <input
                                    type="text"
                                    id="lastName"
                                    name="lastName"
                                    value={formData.lastName}
                                    onChange={handleInputChange}
                                    required
                                />
                            </div>
                            <div className="form-group">
                                <label htmlFor="dateOfBirth">Date of Birth:</label>
                                <input
                                    type="date"
                                    id="dateOfBirth"
                                    name="dateOfBirth"
                                    value={formData.dateOfBirth}
                                    onChange={handleInputChange}
                                    required
                                />
                            </div>
                            <div className="form-group">
                                <label htmlFor="country">Country:</label>
                                <input
                                    type="text"
                                    id="country"
                                    name="country"
                                    value={formData.country}
                                    onChange={handleInputChange}
                                    required
                                />
                            </div>
                            <button type="submit" className="submit-button">Save</button>
                            <button type="button" className="cancel-button" onClick={() => setIsEditing(false)}>Cancel</button>
                        </form>
                    )}
                </>
            ) : (
                <p>Loading user data...</p>
            )}
        </div>
    );
};

export default FanPage;
