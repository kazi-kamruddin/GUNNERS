import NavBar from "./components/NavBar";
import { Route, Routes } from "react-router-dom";
import Dashboard from "./pages/Dashboard/Dashboard.jsx";
import Login from "./pages/Login.jsx";
import Homepage from "./pages/Homepage.jsx";
import Teams from "./pages/teams/teams.jsx";
import ShopPage from './pages/Shop/ShopPage.jsx';

const App = () => {
  return (
    <>
      <NavBar />
      <div style={{ marginTop: "100px" }}>
        <Routes>
          <Route path="/" element={<Homepage />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="login" element={<Login />} />
          <Route path="teams" element={<Teams />} />
          <Route path="shop" element={<ShopPage />} />
        </Routes>
      </div>
    </>
  );
};

export default App;
