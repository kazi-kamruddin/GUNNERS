import React from 'react';
import './dashboard.css'; // import the CSS file

const FanPage = () => {
  const user = {
    name: 'Kazi Kamruddin Ahmed',
    image: 'https://images.unsplash.com/photo-1633332755192-727a05c4013d?q=80&w=1160&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D', // replace with the image URL
  };

  return (
    <div className="fan-page">
      <img src="https://upload.wikimedia.org/wikipedia/hif/8/82/Arsenal_FC.png" alt="Arsenal Logo" className="logo" />
      <h1 className="accent">MY PROFILE</h1>
      <div className="user-profile">
        <img src={user.image} alt={user.name} />
        <h2 className="accent">{user.name}</h2>
        <div className="buttons">
          <button className="edit-button">Edit</button>
          <button className="logout-button">Log Out</button>
        </div>
      </div>
      <div className="menu-bar">
        <ul>
          
          <li><a href="https://www.arsenal.com/news">NEWS</a></li>
          <li><a href="https://www.arsenal.com/fixtures">FIXTURES</a></li>
          <li><a href="https://www.arsenal.com/history">HISTORY</a></li>
        </ul>
      </div>
    </div>
  );
};

export default FanPage;