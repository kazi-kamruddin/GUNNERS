import React from "react";
import "./homePage/homeStyle.css";

const Homepage = () => {
  return (
    <div className="home-body">
      <h1 className="home-h1">Welcome to Our Homepage!</h1>
      <p className="home-p">Here are some of our featured items:</p>
      <div className="home-item-container">
        <div className="home-column">
          <div className="home-item home-item-large">
            <h2 className="home-item-h2">Large Item</h2>
            <p className="home-item-p">Description of Large Item</p>
            <button className="home-item-button">Buy Now</button>
          </div>
        </div>
        <div className="home-column">
          <div className="home-item home-item-small">
            <h2 className="home-item-h2">Small Item 1</h2>
            <p className="home-item-p">Description of Small Item 1</p>
            <button className="home-item-button">Buy Now</button>
          </div>
          <div className="home-item home-item-small">
            <h2 className="home-item-h2">Small Item 2</h2>
            <p className="home-item-p">Description of Small Item 2</p>
            <button className="home-item-button">Buy Now</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Homepage;