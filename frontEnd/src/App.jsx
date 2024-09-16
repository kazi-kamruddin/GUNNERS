import NavBar from "./components/NavBar";
import Footer from "./components/footer"; 
import { Routes, Route, Navigate } from "react-router-dom";
import { useAuthContext } from "./hook/useAuthContext.jsx";
import config from "./config.jsx";
import AdminDashboard from "./pages/adminDashboard.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Homepage from "./pages/Homepage.jsx";
import Teams from "./pages/teams.jsx";
import ShopPage from './pages/ShopPage.jsx';
import Scores from "./pages/scores.jsx";
import Fixture from "./pages/fixture.jsx";
import NewsPage from './pages/news.jsx';
import SingleNews from "./components/singleNews.jsx";
import EditNews from "./components/admin/editNews.jsx";
import EditSingleNews from "./components/admin/editSingleNews.jsx";
import EditPlayerList from "./components/admin/editPlayerList.jsx";
import EditShopItem from "./components/admin/editShopItem.jsx";
import EditFixture from "./components/admin/editFixture.jsx";
import EditScores from "./components/admin/editScores.jsx";
import Login from "./pages/loginPage.jsx";
import SignUp from "./pages/signUpPage.jsx";
import Achievements from "./pages/achievement.jsx";

const App = () => {

  const { user } = useAuthContext();
  let isAdmin = false;

  if(user && user.email === config.ADMIN_EMAIL){
    console.log('admin detected');
    isAdmin = true;
  }
  else if(user){
    console.log('general user detected');
    isAdmin = false;
  }
  else {
    console.log('no user detected');
    isAdmin = false;
  }

  return (
    <>
      <NavBar />
      <div className="content">
        <Routes>
          <Route path="/dashboard" element={user ? <Dashboard /> : <Navigate to={"/login"} />} />
          <Route path="/teams" element={<Teams />} />
          <Route path="/shop" element={<ShopPage />} />
          <Route path="/news" element={<NewsPage />} />
          <Route path="/fixture" element={<Fixture />} />
          <Route path="/scores" element={<Scores />} />
          <Route path="/news/:id" element={<SingleNews />} />
          <Route path="/login" element={!user ? <Login /> : <Navigate to={"/"} />} />
          <Route path="/signUp" element={!user ? <SignUp /> : <Navigate to={"/"} />} />
          <Route path="/" element={<Homepage />} /> 
          <Route path="/achievements" element={<Achievements />} />
          <Route path="/adminDashboard" element={isAdmin ? <AdminDashboard /> : <Navigate to={"/login"} />} />
          <Route path="/adminDashboard/editNews" element={isAdmin ? <EditNews /> : <Navigate to={"/login"} />} />
          <Route path="/adminDashboard/editNews/:id" element={isAdmin ? <EditSingleNews /> : <Navigate to={"/login"} />} />
          <Route path="/adminDashboard/editShop" element={isAdmin ? <EditShopItem /> : <Navigate to={"/login"} />} />
          <Route path="/adminDashboard/editPlayers" element={isAdmin ? <EditPlayerList /> : <Navigate to={"/login"} />} />
          <Route path="/adminDashboard/editFixture" element={isAdmin ? <EditFixture /> : <Navigate to={"/login"} />} />
          <Route path="/adminDashboard/editScores" element={isAdmin ? <EditScores /> : <Navigate to={"/login"} />} />
        </Routes>
      </div>
      <Footer />
    </>
  );
};

export default App;
