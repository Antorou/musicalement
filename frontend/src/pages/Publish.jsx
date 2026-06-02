import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/client";

export default function Publish() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  async function handlePublish() {
    setLoading(true);
    setError(null);
    try {
      await api.post("/posts/");
      navigate("/");
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (detail === "already_posted_today") {
        setError("You already shared a track today. Come back tomorrow!");
      } else if (detail === "no_track") {
        setError("Spotify says you're not playing anything right now. Play something and try again.");
      } else {
        setError("Something went wrong. Try again.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ textAlign: "center", marginTop: "4rem" }}>
      <h2>Share what you're listening to</h2>
      <p>We'll grab your current (or most recent) Spotify track.</p>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <button onClick={handlePublish} disabled={loading}>
        {loading ? "Grabbing track…" : "Share now"}
      </button>
    </div>
  );
}
