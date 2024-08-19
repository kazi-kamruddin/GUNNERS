import NavBar from "./components/NavBar";
import { Routes, Route, Navigate } from "react-router-dom";
import { useAuthContext } from "./hook/useAuthContext.jsx";
import AdminDashboard from "./pages/adminDashboard.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Homepage from "./pages/Homepage.jsx";
import Teams from "./pages/teams.jsx";
import ShopPage from './pages/ShopPage.jsx';
import NewsPage from './pages/news.jsx';
import SingleNews from "./components/singleNews.jsx";
import Login from "./pages/loginPage.jsx";
import SignUp from "./pages/signUpPage.jsx";
import config from "./config.jsx";

const App = () => {

  const { user } = useAuthContext();
  //console.log(user);
  console.log(config.ADMIN_EMAIL);
  console.log("[{()}]");
  if(user){
    console.log(user.email);
  }

  return (
    <>
      <NavBar />
      <div style={{ marginTop: "100px" }}>
        <Routes>
          <Route path="/" element={<Homepage />} />
          <Route path="/dashboard" element={user ? <Dashboard /> : <Navigate to={"/login"}/>} />
          <Route path="/adminDashboard" element={user ? <AdminDashboard /> : <Navigate to={"/login"}/>} />
          <Route path="/teams" element={<Teams />} />
          <Route path="/shop" element={<ShopPage />} />
          <Route path="/news" element={<NewsPage />} />
          <Route path="/news/:id" element={<SingleNews />} />
          <Route path="/login" element={!user ? <Login /> : <Navigate to={"/"}/>} />
          <Route path="/signUp" element={!user  ? <SignUp /> : <Navigate to={"/"}/>} />
        </Routes>
      </div>
    </>
  );
};

export default App;
