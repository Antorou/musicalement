import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/client";
import PostCard from "../components/PostCard";
import Navbar from "../components/Navbar";

export default function Feed() {
  const [posts, setPosts] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get("/posts/feed/")
      .then(({ data }) => setPosts(data))
      .catch((err) => {
        if (err.response?.data?.detail === "post_required") {
          setError("post_required");
        } else {
          setError("unknown");
        }
      })
      .finally(() => setLoading(false));
  }, []);

  function handleLikeToggle(postId) {
    setPosts((prev) =>
      prev.map((p) => {
        if (p.id !== postId) return p;
        const liked = !p.liked_by_me;
        return { ...p, liked_by_me: liked, likes_count: liked ? p.likes_count + 1 : p.likes_count - 1 };
      })
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <Navbar />
      <main className="max-w-2xl mx-auto px-4 py-8">
        {loading && (
          <div className="flex justify-center py-20">
            <div className="w-6 h-6 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
          </div>
        )}

        {!loading && error === "post_required" && (
          <div className="text-center py-20">
            <p className="text-4xl mb-4">🎵</p>
            <h2 className="text-xl font-semibold mb-2">Share first, then see</h2>
            <p className="text-gray-400 mb-6">
              Post today&apos;s track to unlock your friends&apos; feed.
            </p>
            <Link
              to="/publish"
              className="inline-block px-6 py-2.5 bg-violet-600 hover:bg-violet-500 rounded-xl font-medium transition-colors"
            >
              Share now
            </Link>
          </div>
        )}

        {!loading && error === "unknown" && (
          <p className="text-center text-gray-500 py-20">Something went wrong.</p>
        )}

        {!loading && !error && (
          <>
            <h1 className="text-2xl font-bold mb-6">Today&apos;s feed</h1>
            {posts.length === 0 ? (
              <div className="text-center py-20">
                <p className="text-4xl mb-4">👋</p>
                <p className="text-gray-400 mb-4">No posts yet — add some friends!</p>
                <Link
                  to="/friends"
                  className="inline-block px-6 py-2.5 bg-gray-800 hover:bg-gray-700 rounded-xl font-medium transition-colors"
                >
                  Find friends
                </Link>
              </div>
            ) : (
              <div className="space-y-4">
                {posts.map((p) => (
                  <PostCard key={p.id} post={p} onLikeToggle={handleLikeToggle} />
                ))}
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}
