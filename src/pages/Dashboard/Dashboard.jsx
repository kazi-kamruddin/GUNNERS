import React, { useState } from 'react';
import './dashboard.css'; // import the CSS file
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';

const FanPage = () => {
  const user = {
    name: 'Kazi Kamruddin Ahmed',
    image: 'https://images.unsplash.com/photo-1633332755192-727a05c4013d?q=80&w=1160&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D', // replace with the image URL
  };

  const [isEditing, setIsEditing] = useState(false);
  const [formErrors, setFormErrors] = useState({});

  const handleEditClick = () => {
    setIsEditing(true);
  };

  const handleSaveClick = () => {
    const form = document.querySelector('.edit-form');
    const isValid = form.checkValidity();

    if (isValid) {
      setIsEditing(false);
    } else {
      setFormErrors(validateForm());
    }
  };

  const handleCancelClick = () => {
    setIsEditing(false);
  };

  const validateForm = () => {
    const errors = {};
    const inputs = document.querySelectorAll('.edit-form input, .edit-form select');

    inputs.forEach((input) => {
      if (!input.value) {
        errors[input.id] = `${input.id.charAt(0).toUpperCase()}${input.id.slice(1)} is required`;
      }
    });

    return errors;
  };

  return (
    <div className="fan-page">
      <img src="https://upload.wikimedia.org/wikipedia/hif/8/82/Arsenal_FC.png" alt="Arsenal Logo" className="logo" />
      <h1 className="accent">MY PROFILE</h1>
      <div className="user-profile">
        <img src={user.image} alt={user.name} />
        <h2 className="accent">{user.name}</h2>
        <div className="buttons">
          <button className="edit-button" onClick={handleEditClick}>Edit</button>
          <button className="logout-button">Log Out</button>
        </div>
      </div>
      <div className="menu-bar">
        <ul>
          <li><a href="https://www.arsenal.com/news" >NEWS</a></li>
          <li><a href="https://www.arsenal.com/fixtures">FIXTURES</a></li>
          <li><a href="https://www.arsenal.com/history">HISTORY</a></li>
        </ul>
      </div>
      {isEditing && (
        <div className="edit-form-container">
          <form className="edit-form" noValidate>
            <label htmlFor="gender">Gender:</label>
            <select id="gender">
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
            </select>
            {formErrors.gender && <p className="error">{formErrors.gender}</p>}
            <label htmlFor="first-name">First Name:</label>
            <input type="text" id="first-name" required />
            {formErrors.firstName && <p className="error">{formErrors.firstName}</p>}
            <label htmlFor="last-name">Last Name:</label>
            <input type="text" id="last-name" required />
            {formErrors.lastName && <p className="error">{formErrors.lastName}</p>}
            <label htmlFor="dob">Date of Birth:</label>
            <input type="date" id="dob" required />
            {formErrors.dob && <p className="error">{formErrors.dob}</p>}
            <label htmlFor="country">Country:</label>
            <input type="text" id="country" required />
            {formErrors.country && <p className="error">{formErrors.country}</p>}
            <label htmlFor="email">Email Address:</label>
            <input type="email" id="email" required />
            {formErrors.email && <p className="error">{formErrors.email}</p>}
            <button type="button" onClick={handleSaveClick}>Save</button>
            <button type="button" onClick={handleCancelClick}>Cancel</button>
          </form>
        </div>
      )}
      <footer>
        <p>&copy; 2023 Arsenal FC Fan Page</p>
        <div className="social-media">
          <>
          <FontAwesomeIcon icon="fa-brands fa-square-facebook" />
          </>
          <a href="https://www.instagram.com" target="_blank" rel="noopener noreferrer">
            <i className="fab fa-instagram"></i>
          </a>
        </div>
      </footer>
    </div>
  );
};

export default FanPage;
