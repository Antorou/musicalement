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
    <div className="min-h-screen bg-gray-950 text-white flex flex-col items-center justify-center px-4">
      <h1 className="text-4xl font-bold text-violet-400 mb-2 tracking-tight">musicalement</h1>
      <p className="text-gray-400 mb-8">Share what you&apos;re listening to, once a day.</p>
      <a href="/api/v1/auth/spotify/">
        <button className="px-8 py-3 bg-violet-600 hover:bg-violet-500 rounded-xl font-semibold text-white transition-colors">
          Connect with Spotify
        </button>
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
          path="/profile"
          element={
            <PrivateRoute>
              <Profile />
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
