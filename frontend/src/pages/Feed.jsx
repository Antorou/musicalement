import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/client";
import PostCard from "../components/PostCard";

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
        return {
          ...p,
          liked_by_me: liked,
          likes_count: liked ? p.likes_count + 1 : p.likes_count - 1,
        };
      })
    );
  }

  if (loading) return <p>Loading…</p>;

  if (error === "post_required") {
    return (
      <div style={{ textAlign: "center", marginTop: "4rem" }}>
        <p>You need to post today before you can see your friends' posts.</p>
        <Link to="/publish">
          <button>Share now</button>
        </Link>
      </div>
    );
  }

  if (error) return <p>Something went wrong.</p>;

  return (
    <div style={{ maxWidth: 600, margin: "0 auto", padding: "1rem" }}>
      <nav style={{ display: "flex", gap: "1rem", marginBottom: "1rem" }}>
        <Link to="/publish">Share today's track</Link>
        <Link to="/friends">Friends</Link>
      </nav>
      {posts.length === 0 ? (
        <p>No posts yet. Add some friends!</p>
      ) : (
        posts.map((p) => (
          <PostCard key={p.id} post={p} onLikeToggle={handleLikeToggle} />
        ))
      )}
    </div>
  );
}
