import { useState } from "react";
import { Routes, Route, Link } from "react-router";
import RegisterPackagePage from './pages/RegisterPackagePage.jsx';
import PackageDetailPage from './pages/PackageDetailPage.jsx';
import LoginPage from './frontend/src/pages/LoginPage.jsx';
import RegisterUserPage from './pages/RegisterUserPage.jsx';

function App() {
  const [token, setToken] = useState("");

  return (
    <>
      <nav>
        <Link to="/register">Register</Link> |{" "}
        <Link to="/login">Login</Link> |{" "}
        <Link to="/">Packages</Link>
      </nav>
      <Routes>
        <Route path="/" element={<RegisterPackagePage token={token} />} />
        <Route path="/packages/:id" element={<PackageDetailPage token={token} />} />
        <Route path="/login" element={<LoginPage setToken={setToken} />} />
        <Route path="/register" element={<RegisterUserPage />} />
        <Route path="*" element={<h1>404 Not Found</h1>} />
      </Routes>
    </>
  );
}

export default App;