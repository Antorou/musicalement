import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/client";
import Navbar from "../components/Navbar";

export default function Publish() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [selected, setSelected] = useState(null);
  const [searching, setSearching] = useState(false);
  const [publishing, setPublishing] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  // Guards against out-of-order responses: only the latest request wins
  const latestQuery = useRef("");

  // Search as you type, debounced so we don't hit Spotify on every keystroke
  useEffect(() => {
    const q = query.trim();
    latestQuery.current = q;

    if (!q) {
      setResults([]);
      setSearching(false);
      return;
    }

    setSearching(true);
    const handle = setTimeout(async () => {
      try {
        const { data } = await api.get(`/posts/search-tracks/?q=${encodeURIComponent(q)}`);
        if (latestQuery.current === q) {
          setResults(data.results);
          setError(null);
        }
      } catch {
        if (latestQuery.current === q) setError("Search failed. Try again.");
      } finally {
        if (latestQuery.current === q) setSearching(false);
      }
    }, 350);

    return () => clearTimeout(handle);
  }, [query]);

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
    <div className="min-h-screen bg-gray-950 text-white">
      <Navbar />
      <main className="max-w-2xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-2">What are you listening to?</h1>
        <p className="text-gray-400 mb-6">One track, once a day.</p>

        <div className="relative mb-6">
          <input
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setSelected(null);
            }}
            placeholder="Search for a track or artist…"
            autoFocus
            className="w-full bg-gray-900 border border-white/10 rounded-xl px-4 py-2.5 pr-10 text-white placeholder-gray-600 focus:outline-none focus:border-violet-500"
          />
          {searching && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
          )}
        </div>

        {error && (
          <p className="text-red-400 text-sm mb-4">{error}</p>
        )}

        {results.length > 0 && (
          <ul className="space-y-2 mb-6">
            {results.map((track) => (
              <li
                key={track.spotify_track_id}
                onClick={() => setSelected(track)}
                className={`flex items-center gap-3 p-3 rounded-xl cursor-pointer border transition-all ${
                  selected?.spotify_track_id === track.spotify_track_id
                    ? "border-violet-500 bg-violet-500/10"
                    : "border-white/5 bg-gray-900 hover:border-white/20"
                }`}
              >
                {track.album_cover_url && (
                  <img
                    src={track.album_cover_url}
                    alt="album"
                    className="w-12 h-12 rounded-lg object-cover flex-shrink-0"
                  />
                )}
                <div className="min-w-0">
                  <p className="font-medium truncate">{track.track_title}</p>
                  <p className="text-sm text-gray-400 truncate">
                    {track.artist_name} — {track.album_name}
                  </p>
                </div>
                {selected?.spotify_track_id === track.spotify_track_id && (
                  <span className="ml-auto text-violet-400 flex-shrink-0">✓</span>
                )}
              </li>
            ))}
          </ul>
        )}

        {query.trim() && !searching && results.length === 0 && !error && (
          <p className="text-gray-500 text-sm mb-6">No tracks found for {query.trim()}.</p>
        )}

        {selected && (
          <button
            onClick={handlePublish}
            disabled={publishing}
            className="w-full py-3 bg-violet-600 hover:bg-violet-500 disabled:opacity-50 rounded-xl font-semibold transition-colors"
          >
            {publishing ? "Sharing…" : `Share "${selected.track_title}"`}
          </button>
        )}
      </main>
    </div>
  );
}
