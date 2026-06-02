import { Link, useLocation } from "react-router-dom";

const links = [
  { to: "/", label: "Feed" },
  { to: "/publish", label: "Share" },
  { to: "/friends", label: "Friends" },
  { to: "/profile", label: "Profile" },
];

export default function Navbar() {
  const { pathname } = useLocation();

  function handleLogout() {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    window.location.href = "/login";
  }

  return (
    <nav className="sticky top-0 z-50 bg-gray-950/80 backdrop-blur border-b border-white/5">
      <div className="max-w-2xl mx-auto flex items-center justify-between px-4 py-3">
        <Link to="/" className="text-violet-400 font-bold tracking-tight text-lg">
          musicalement
        </Link>
        <div className="flex items-center gap-1">
          {links.map(({ to, label }) => (
            <Link
              key={to}
              to={to}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                pathname === to
                  ? "bg-violet-500/20 text-violet-300"
                  : "text-gray-400 hover:text-white hover:bg-white/5"
              }`}
            >
              {label}
            </Link>
          ))}
          <button
            onClick={handleLogout}
            className="ml-2 px-3 py-1.5 rounded-lg text-sm font-medium text-gray-500 hover:text-red-400 hover:bg-red-400/10 transition-colors"
          >
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}
