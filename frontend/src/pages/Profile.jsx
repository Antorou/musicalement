import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../api/client";
import PostCard from "../components/PostCard";

export default function Profile() {
  const { id } = useParams();
  const [user, setUser] = useState(null);
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get(`/users/${id}/`),
      api.get(`/posts/feed/?user=${id}`),
    ])
      .then(([userRes, postsRes]) => {
        setUser(userRes.data);
        setPosts(postsRes.data);
      })
      .finally(() => setLoading(false));
  }, [id]);

  function handleLikeToggle(postId) {
    setPosts((prev) =>
      prev.map((p) => {
        if (p.id !== postId) return p;
        const liked = !p.liked_by_me;
        return { ...p, liked_by_me: liked, likes_count: liked ? p.likes_count + 1 : p.likes_count - 1 };
      })
    );
  }

  if (loading) return <p>Loading…</p>;
  if (!user) return <p>User not found.</p>;

  return (
    <div style={{ maxWidth: 600, margin: "0 auto", padding: "1rem" }}>
      <h2>{user.username}</h2>
      {user.avatar_url && <img src={user.avatar_url} alt="avatar" width={64} />}
      <hr />
      {posts.length === 0 ? (
        <p>No posts yet.</p>
      ) : (
        posts.map((p) => <PostCard key={p.id} post={p} onLikeToggle={handleLikeToggle} />)
      )}
    </div>
  );
}
