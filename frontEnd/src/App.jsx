import NavBar from "./components/NavBar";
import { Routes, Route } from "react-router-dom";
import Dashboard from "./pages/Dashboard.jsx";
import LoginG from "./pages/Login.jsx";
import Homepage from "./pages/Homepage.jsx";
import Teams from "./pages/teams.jsx";
import ShopPage from './pages/ShopPage.jsx';
import NewsPage from './pages/news.jsx';
import SingleNews from "./components/singleNews.jsx";
import Login from "./pages/loginPage.jsx";
import SignUp from "./pages/signUpPage.jsx";

const App = () => {
  return (
    <>
      <NavBar />
      <div style={{ marginTop: "100px" }}>
        <Routes>
          <Route path="/" element={<Homepage />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="teams" element={<Teams />} />
          <Route path="shop" element={<ShopPage />} />
          <Route path="news" element={<NewsPage />} />
          <Route path="news/:id" element={<SingleNews />} />
          <Route path="login" element={<Login />} />
          <Route path="signUp" element={<SignUp />} />
        </Routes>
      </div>
    </>
  );
};

export default App;
