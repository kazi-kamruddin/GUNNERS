import NavBar from "./components/NavBar";
import { Route, Routes } from "react-router-dom";
import Dashboard from "./pages/Dashboard.jsx";
import Login from "./pages/Login.jsx";
import Homepage from "./pages/Homepage.jsx";

const App = () => {
  return (
    <>
      <NavBar />
      <div style={{ marginTop: "100px" }}>
        <Routes>
          <Route path="/" element={<Homepage />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="login" element={<Login />} />
        </Routes>
      </div>
    </>
  );
};

export default App;
