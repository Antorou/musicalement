import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/client";
import Navbar from "../components/Navbar";

function getOtherUser(friendship, currentUserId) {
  return friendship.from_user.id === currentUserId
    ? friendship.to_user
    : friendship.from_user;
}

export default function Friends() {
  const [friendships, setFriendships] = useState([]);
  const [currentUserId, setCurrentUserId] = useState(null);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.get("/users/me/"), api.get("/friendships/")])
      .then(([meRes, fsRes]) => {
        setCurrentUserId(meRes.data.id);
        setFriendships(fsRes.data);
      })
      .finally(() => setLoading(false));
  }, []);

  async function search(e) {
    e.preventDefault();
    if (!query.trim()) return;
    const { data } = await api.get(`/users/?search=${encodeURIComponent(query)}`);
    setResults(data);
  }

  async function sendRequest(userId) {
    try {
      await api.post("/friendships/", { to_user_id: userId });
      setResults((prev) => prev.filter((u) => u.id !== userId));
      const { data } = await api.get("/friendships/");
      setFriendships(data);
    } catch (err) {
      alert(err.response?.data?.detail || "Could not send request.");
    }
  }

  async function respond(id, action) {
    if (action === "accept") {
      await api.patch(`/friendships/${id}/`, { status: "accepted" });
    } else {
      await api.delete(`/friendships/${id}/`);
    }
    const { data } = await api.get("/friendships/");
    setFriendships(data);
  }

  const incoming = friendships.filter(
    (f) => f.status === "pending" && f.to_user.id === currentUserId
  );
  const outgoing = friendships.filter(
    (f) => f.status === "pending" && f.from_user.id === currentUserId
  );
  const accepted = friendships.filter((f) => f.status === "accepted");

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <Navbar />
      <main className="max-w-2xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-6">Friends</h1>

        {loading ? (
          <div className="flex justify-center py-20">
            <div className="w-6 h-6 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : (
          <>
            <form onSubmit={search} className="flex gap-2 mb-6">
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search by username…"
                className="flex-1 bg-gray-900 border border-white/10 rounded-xl px-4 py-2.5 text-white placeholder-gray-600 focus:outline-none focus:border-violet-500"
              />
              <button
                type="submit"
                className="px-5 py-2.5 bg-violet-600 hover:bg-violet-500 rounded-xl font-medium transition-colors"
              >
                Search
              </button>
            </form>

            {results.length > 0 && (
              <div className="space-y-2 mb-6">
                {results.map((u) => (
                  <div
                    key={u.id}
                    className="flex items-center justify-between bg-gray-900 border border-white/5 rounded-xl px-4 py-3"
                  >
                    <span className="font-medium">{u.username}</span>
                    <button
                      onClick={() => sendRequest(u.id)}
                      className="px-4 py-1.5 bg-violet-600 hover:bg-violet-500 rounded-lg text-sm font-medium transition-colors"
                    >
                      Add
                    </button>
                  </div>
                ))}
              </div>
            )}

            {incoming.length > 0 && (
              <section className="mb-6">
                <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">
                  Requests received ({incoming.length})
                </h2>
                <div className="space-y-2">
                  {incoming.map((f) => (
                    <div
                      key={f.id}
                      className="flex items-center justify-between bg-gray-900 border border-violet-500/20 rounded-xl px-4 py-3"
                    >
                      <span className="font-medium">{f.from_user.username}</span>
                      <div className="flex gap-2">
                        <button
                          onClick={() => respond(f.id, "accept")}
                          className="px-3 py-1.5 bg-violet-600 hover:bg-violet-500 rounded-lg text-sm font-medium transition-colors"
                        >
                          Accept
                        </button>
                        <button
                          onClick={() => respond(f.id, "decline")}
                          className="px-3 py-1.5 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm font-medium transition-colors"
                        >
                          Decline
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {outgoing.length > 0 && (
              <section className="mb-6">
                <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">
                  Requests sent ({outgoing.length})
                </h2>
                <div className="space-y-2">
                  {outgoing.map((f) => (
                    <div
                      key={f.id}
                      className="flex items-center justify-between bg-gray-900 border border-white/5 rounded-xl px-4 py-3"
                    >
                      <span className="font-medium">{f.to_user.username}</span>
                      <span className="text-xs text-gray-500 bg-gray-800 px-2 py-1 rounded-full">
                        pending
                      </span>
                    </div>
                  ))}
                </div>
              </section>
            )}

            <section>
              <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">
                Friends ({accepted.length})
              </h2>
              {accepted.length === 0 ? (
                <p className="text-gray-500 text-sm">No friends yet. Search above to add some!</p>
              ) : (
                <div className="space-y-2">
                  {accepted.map((f) => {
                    const other = getOtherUser(f, currentUserId);
                    return (
                      <Link
                        key={f.id}
                        to={`/profile/${other.id}`}
                        className="flex items-center gap-3 bg-gray-900 border border-white/5 hover:border-violet-500/30 rounded-xl px-4 py-3 transition-colors"
                      >
                        {other.avatar_url ? (
                          <img
                            src={other.avatar_url}
                            alt={other.username}
                            className="w-8 h-8 rounded-full object-cover"
                          />
                        ) : (
                          <div className="w-8 h-8 rounded-full bg-violet-500/20 flex items-center justify-center text-violet-400 text-xs font-bold">
                            {other.username[0].toUpperCase()}
                          </div>
                        )}
                        <span className="font-medium">{other.username}</span>
                      </Link>
                    );
                  })}
                </div>
              )}
            </section>
          </>
        )}
      </main>
    </div>
  );
}
