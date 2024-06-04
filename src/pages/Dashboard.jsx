import React, { useState } from "react";
import Button from "../components/Button";

const Dashboard = () => {
  const [count, setCount] = useState(0);

  const increment = () => {
    setCount((prev) => prev + 1);
  };

  return (
    <div style={{ textAlign: "center" }}>
      <h1>This is dashboard</h1>
      <p style={{ fontSize: "25px" }}>{`Value of count is: ${count}`}</p>
      <div>
        <Button btnText="Increment" onClick={increment} />
      </div>
    </div>
  );
};

export default Dashboard;
