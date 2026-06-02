import { useEffect, useState } from "react";
import api from "../api/client";

export default function Friends() {
  const [friendships, setFriendships] = useState([]);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get("/friendships/")
      .then(({ data }) => setFriendships(data))
      .finally(() => setLoading(false));
  }, []);

  async function search(e) {
    e.preventDefault();
    if (!query.trim()) return;
    const { data } = await api.get(`/users/?search=${encodeURIComponent(query)}`);
    setResults(data);
  }

  async function sendRequest(userId) {
    await api.post("/friendships/", { to_user: userId });
    setResults((prev) => prev.filter((u) => u.id !== userId));
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

  const pending = friendships.filter((f) => f.status === "pending");
  const accepted = friendships.filter((f) => f.status === "accepted");

  return (
    <div style={{ maxWidth: 600, margin: "0 auto", padding: "1rem" }}>
      <h2>Friends</h2>

      <form onSubmit={search} style={{ marginBottom: "1rem" }}>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search by username…"
        />
        <button type="submit">Search</button>
      </form>

      {results.map((u) => (
        <div key={u.id} style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.5rem" }}>
          <span>{u.username}</span>
          <button onClick={() => sendRequest(u.id)}>Add</button>
        </div>
      ))}

      {pending.length > 0 && (
        <>
          <h3>Pending requests</h3>
          {pending.map((f) => (
            <div key={f.id} style={{ display: "flex", gap: "0.5rem", marginBottom: "0.5rem" }}>
              <span>{f.from_user_username}</span>
              <button onClick={() => respond(f.id, "accept")}>Accept</button>
              <button onClick={() => respond(f.id, "decline")}>Decline</button>
            </div>
          ))}
        </>
      )}

      <h3>Friends ({accepted.length})</h3>
      {accepted.length === 0 ? (
        <p>No friends yet. Search above to add some!</p>
      ) : (
        accepted.map((f) => (
          <div key={f.id} style={{ marginBottom: "0.5rem" }}>
            {f.from_user_username === undefined ? f.to_user_username : f.from_user_username}
          </div>
        ))
      )}
    </div>
  );
}
