import { useState } from "react";
import api from "../api/client";

export default function PostCard({ post, onLikeToggle }) {
  const [comments, setComments] = useState(post.comments ?? []);
  const [body, setBody] = useState("");
  const [showComments, setShowComments] = useState(false);

  async function handleLike() {
    await api.post(`/posts/${post.id}/like/`);
    onLikeToggle(post.id);
  }

  async function loadComments() {
    const { data } = await api.get(`/posts/${post.id}/comments/`);
    setComments(data);
    setShowComments(true);
  }

  async function handleComment(e) {
    e.preventDefault();
    if (!body.trim()) return;
    const { data } = await api.post(`/posts/${post.id}/comments/`, { body });
    setComments((prev) => [...prev, data]);
    setBody("");
  }

  return (
    <div style={{ border: "1px solid #ccc", padding: "1rem", marginBottom: "1rem" }}>
      <strong>{post.user?.username}</strong>
      <p>
        {post.track_title} — {post.artist_name}
      </p>
      {post.album_cover_url && (
        <img src={post.album_cover_url} alt="album art" width={80} />
      )}
      <p style={{ fontSize: "0.85rem", color: "#666" }}>
        {post.likes_count} like{post.likes_count !== 1 ? "s" : ""}
      </p>
      <button onClick={handleLike}>{post.liked_by_me ? "Unlike" : "Like"}</button>{" "}
      <button onClick={showComments ? () => setShowComments(false) : loadComments}>
        {showComments ? "Hide comments" : `Comments (${post.comments_count})`}
      </button>
      {showComments && (
        <div style={{ marginTop: "0.5rem" }}>
          {comments.map((c) => (
            <p key={c.id} style={{ margin: "0.25rem 0" }}>
              <strong>{c.user?.username}</strong>: {c.body}
            </p>
          ))}
          <form onSubmit={handleComment}>
            <input
              value={body}
              onChange={(e) => setBody(e.target.value)}
              placeholder="Add a comment…"
              maxLength={280}
            />
            <button type="submit">Post</button>
          </form>
        </div>
      )}
    </div>
  );
}
