import "../src/components/Styles/Main.css";
import HomePage from "./components/HomePage/HomePage.jsx";
import RegistrationPage from "./components/RegistrationPage/RegistrationPage.jsx";
import LoginPage from "./components/LoginPage/LoginPage.jsx";
import { Routes, Route, useLocation } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoutes/ProtectedRoutes.jsx";
import Navbar from "./components/Navbar/Navbar.jsx";

function App() {
  const location = useLocation();
  const noNavbar =
    location.pathname === "/register" ||
    location.pathname === "/" ||
    location.pathname.includes("password");

  return (
    <>
      {noNavbar ? (
        <Routes>
          <Route path="/" element={<LoginPage />} />
          <Route path="/register" element={<RegistrationPage />} />
          
        </Routes>
      ) : (
        <Navbar
          content={
            <Routes>
              <Route element={<ProtectedRoute />}>
                <Route path="/home" element={<HomePage />} />
              </Route>
            </Routes>
          }
        />
      )}
    </>
  );
}

export default App;
