import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/client";

export default function Publish() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [selected, setSelected] = useState(null);
  const [searching, setSearching] = useState(false);
  const [publishing, setPublishing] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  async function handleSearch(e) {
    e.preventDefault();
    if (!query.trim()) return;
    setSearching(true);
    setSelected(null);
    setError(null);
    try {
      const { data } = await api.get(`/posts/search-tracks/?q=${encodeURIComponent(query)}`);
      setResults(data.results);
    } catch {
      setError("Search failed. Try again.");
    } finally {
      setSearching(false);
    }
  }

  async function handlePublish() {
    if (!selected) return;
    setPublishing(true);
    setError(null);
    try {
      await api.post("/posts/", { spotify_track_id: selected.spotify_track_id });
      navigate("/");
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (detail === "already_posted_today") {
        setError("You already shared a track today. Come back tomorrow!");
      } else {
        setError("Something went wrong. Try again.");
      }
    } finally {
      setPublishing(false);
    }
  }

  return (
    <div style={{ maxWidth: 600, margin: "2rem auto", padding: "1rem" }}>
      <h2>What are you listening to today?</h2>

      <form onSubmit={handleSearch} style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem" }}>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search for a track…"
          style={{ flex: 1, padding: "0.5rem" }}
        />
        <button type="submit" disabled={searching}>
          {searching ? "Searching…" : "Search"}
        </button>
      </form>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {results.length > 0 && (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {results.map((track) => (
            <li
              key={track.spotify_track_id}
              onClick={() => setSelected(track)}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "0.75rem",
                padding: "0.5rem",
                cursor: "pointer",
                borderRadius: 6,
                background: selected?.spotify_track_id === track.spotify_track_id ? "#e8f4ff" : "transparent",
                border: selected?.spotify_track_id === track.spotify_track_id ? "1px solid #0070f3" : "1px solid transparent",
                marginBottom: "0.5rem",
              }}
            >
              {track.album_cover_url && (
                <img src={track.album_cover_url} alt="album" width={48} height={48} style={{ borderRadius: 4 }} />
              )}
              <div>
                <div style={{ fontWeight: 600 }}>{track.track_title}</div>
                <div style={{ fontSize: "0.85rem", color: "#666" }}>{track.artist_name} — {track.album_name}</div>
              </div>
            </li>
          ))}
        </ul>
      )}

      {selected && (
        <div style={{ marginTop: "1rem" }}>
          <p>Sharing: <strong>{selected.track_title}</strong> by {selected.artist_name}</p>
          <button onClick={handlePublish} disabled={publishing}>
            {publishing ? "Sharing…" : "Share now"}
          </button>
        </div>
      )}
    </div>
  );
}
