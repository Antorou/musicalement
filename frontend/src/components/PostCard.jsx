import { useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/client";

export default function PostCard({ post, onLikeToggle, onDelete }) {
  const [comments, setComments] = useState([]);
  const [body, setBody] = useState("");
  const [showComments, setShowComments] = useState(false);
  const [loadingComments, setLoadingComments] = useState(false);

  async function handleLike() {
    await api.post(`/posts/${post.id}/like/`);
    onLikeToggle(post.id);
  }

  async function loadComments() {
    if (showComments) {
      setShowComments(false);
      return;
    }
    setLoadingComments(true);
    const { data } = await api.get(`/posts/${post.id}/comments/`);
    setComments(data);
    setLoadingComments(false);
    setShowComments(true);
  }

  async function handleComment(e) {
    e.preventDefault();
    if (!body.trim()) return;
    const { data } = await api.post(`/posts/${post.id}/comments/`, { body });
    setComments((prev) => [...prev, data]);
    setBody("");
  }

  async function handleCommentLike(commentId) {
    const { data } = await api.post(`/posts/${post.id}/comments/${commentId}/like/`);
    setComments((prev) =>
      prev.map((c) =>
        c.id === commentId
          ? { ...c, liked_by_me: data.liked, likes_count: data.likes_count }
          : c
      )
    );
  }

  return (
    <div className="bg-gray-900 border border-white/5 rounded-2xl overflow-hidden hover:border-violet-500/30 transition-colors">
      <div className="flex gap-4 p-4">
        {post.album_cover_url ? (
          <img
            src={post.album_cover_url}
            alt="album art"
            className="w-20 h-20 rounded-xl object-cover flex-shrink-0 shadow-lg"
          />
        ) : (
          <div className="w-20 h-20 rounded-xl bg-gray-800 flex-shrink-0" />
        )}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div className="min-w-0">
              <p className="font-semibold text-white truncate">{post.track_title}</p>
              <p className="text-sm text-gray-400 truncate">{post.artist_name}</p>
              <p className="text-xs text-gray-600 truncate">{post.album_name}</p>
            </div>
            {post.user && (
              <Link
                to={`/profile/${post.user.id}`}
                className="text-xs text-gray-500 hover:text-violet-400 transition-colors flex-shrink-0"
              >
                {post.user.username}
              </Link>
            )}
          </div>
          {post.note && (
            <p className="mt-2 text-sm text-gray-300 italic">"{post.note}"</p>
          )}
          <div className="flex items-center gap-3 mt-3">
            <button
              onClick={handleLike}
              className={`flex items-center gap-1.5 text-sm transition-colors ${
                post.liked_by_me
                  ? "text-violet-400"
                  : "text-gray-500 hover:text-violet-400"
              }`}
            >
              <span>{post.liked_by_me ? "♥" : "♡"}</span>
              <span>{post.likes_count}</span>
            </button>
            <button
              onClick={loadComments}
              className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-300 transition-colors"
            >
              <span>💬</span>
              <span>{post.comments_count}</span>
            </button>
            {onDelete && (
              <button
                onClick={() => onDelete(post.id)}
                className="ml-auto text-sm text-gray-600 hover:text-red-400 transition-colors"
                title="Delete post"
              >
                🗑
              </button>
            )}
          </div>
        </div>
      </div>

      {showComments && (
        <div className="border-t border-white/5 px-4 pb-4">
          {loadingComments ? (
            <p className="text-xs text-gray-600 pt-3">Loading…</p>
          ) : (
            <>
              <div className="space-y-2 pt-3">
                {comments.length === 0 && (
                  <p className="text-xs text-gray-600">No comments yet.</p>
                )}
                {comments.map((c) => (
                  <div key={c.id} className="flex items-start justify-between gap-2">
                    <p className="text-sm text-gray-300 min-w-0">
                      <span className="text-violet-400 font-medium">{c.user?.username}</span>{" "}
                      {c.body}
                    </p>
                    <button
                      onClick={() => handleCommentLike(c.id)}
                      className={`flex items-center gap-1 text-xs flex-shrink-0 transition-colors ${
                        c.liked_by_me ? "text-violet-400" : "text-gray-600 hover:text-violet-400"
                      }`}
                    >
                      <span>{c.liked_by_me ? "♥" : "♡"}</span>
                      {c.likes_count > 0 && <span>{c.likes_count}</span>}
                    </button>
                  </div>
                ))}
              </div>
              <form onSubmit={handleComment} className="flex gap-2 mt-3">
                <input
                  value={body}
                  onChange={(e) => setBody(e.target.value)}
                  placeholder="Add a comment…"
                  maxLength={280}
                  className="flex-1 bg-gray-800 border border-white/10 rounded-lg px-3 py-1.5 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-violet-500"
                />
                <button
                  type="submit"
                  className="px-3 py-1.5 bg-violet-600 hover:bg-violet-500 rounded-lg text-sm font-medium text-white transition-colors"
                >
                  Post
                </button>
              </form>
            </>
          )}
        </div>
      )}
    </div>
  );
}
