import { useEffect } from "react";
import { BrowserRouter, Routes, Route, useNavigate } from "react-router-dom";
import PrivateRoute from "./components/PrivateRoute";
import Feed from "./pages/Feed";
import Publish from "./pages/Publish";
import Profile from "./pages/Profile";
import Friends from "./pages/Friends";

// Django redirects here after Spotify OAuth: /?token=ACCESS&refresh=REFRESH
function AuthCallback() {
  const navigate = useNavigate();
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const access = params.get("token");
    const refresh = params.get("refresh");
    if (access && refresh) {
      localStorage.setItem("access", access);
      localStorage.setItem("refresh", refresh);
    }
    navigate("/", { replace: true });
  }, [navigate]);
  return null;
}

function LoginPage() {
  return (
    <div style={{ textAlign: "center", marginTop: "4rem" }}>
      <h1>Musicalement</h1>
      <p>Share what you're listening to, once a day.</p>
      <a href="/api/v1/auth/spotify/">
        <button>Connect with Spotify</button>
      </a>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/callback" element={<AuthCallback />} />
        <Route
          path="/"
          element={
            <PrivateRoute>
              <Feed />
            </PrivateRoute>
          }
        />
        <Route
          path="/publish"
          element={
            <PrivateRoute>
              <Publish />
            </PrivateRoute>
          }
        />
        <Route
          path="/profile/:id"
          element={
            <PrivateRoute>
              <Profile />
            </PrivateRoute>
          }
        />
        <Route
          path="/friends"
          element={
            <PrivateRoute>
              <Friends />
            </PrivateRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}
