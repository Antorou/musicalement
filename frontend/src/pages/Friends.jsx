import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/client";

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

  if (loading) return <p>Loading…</p>;

  const incoming = friendships.filter(
    (f) => f.status === "pending" && f.to_user.id === currentUserId
  );
  const outgoing = friendships.filter(
    (f) => f.status === "pending" && f.from_user.id === currentUserId
  );
  const accepted = friendships.filter((f) => f.status === "accepted");

  return (
    <div style={{ maxWidth: 600, margin: "0 auto", padding: "1rem" }}>
      <h2>Friends</h2>
      <Link to="/">Back to feed</Link>

      <form onSubmit={search} style={{ display: "flex", gap: "0.5rem", margin: "1rem 0" }}>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search by username…"
          style={{ flex: 1, padding: "0.5rem" }}
        />
        <button type="submit">Search</button>
      </form>

      {results.map((u) => (
        <div key={u.id} style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.5rem" }}>
          <span>{u.username}</span>
          <button onClick={() => sendRequest(u.id)}>Add</button>
        </div>
      ))}

      {incoming.length > 0 && (
        <>
          <h3>Requests received ({incoming.length})</h3>
          {incoming.map((f) => (
            <div key={f.id} style={{ display: "flex", gap: "0.5rem", alignItems: "center", marginBottom: "0.5rem" }}>
              <span>{f.from_user.username}</span>
              <button onClick={() => respond(f.id, "accept")}>Accept</button>
              <button onClick={() => respond(f.id, "decline")}>Decline</button>
            </div>
          ))}
        </>
      )}

      {outgoing.length > 0 && (
        <>
          <h3>Requests sent ({outgoing.length})</h3>
          {outgoing.map((f) => (
            <div key={f.id} style={{ color: "#999", marginBottom: "0.5rem" }}>
              {f.to_user.username} — pending
            </div>
          ))}
        </>
      )}

      <h3>Friends ({accepted.length})</h3>
      {accepted.length === 0 ? (
        <p>No friends yet. Search above to add some!</p>
      ) : (
        accepted.map((f) => {
          const other = getOtherUser(f, currentUserId);
          return (
            <div key={f.id} style={{ marginBottom: "0.5rem" }}>
              <Link to={`/profile/${other.id}`}>{other.username}</Link>
            </div>
          );
        })
      )}
    </div>
  );
}
