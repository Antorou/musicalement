import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../api/client";
import PostCard from "../components/PostCard";
import Navbar from "../components/Navbar";

export default function Profile() {
  const { id } = useParams();
  const isOwnProfile = !id;

  const [user, setUser] = useState(null);
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const userReq = isOwnProfile ? api.get("/users/me/") : api.get(`/users/${id}/`);
    const postsReq = isOwnProfile ? api.get("/posts/me/") : Promise.resolve({ data: [] });

    Promise.all([userReq, postsReq])
      .then(([userRes, postsRes]) => {
        setUser(userRes.data);
        setPosts(postsRes.data);
      })
      .finally(() => setLoading(false));
  }, [id, isOwnProfile]);

  function handleLikeToggle(postId) {
    setPosts((prev) =>
      prev.map((p) => {
        if (p.id !== postId) return p;
        const liked = !p.liked_by_me;
        return { ...p, liked_by_me: liked, likes_count: liked ? p.likes_count + 1 : p.likes_count - 1 };
      })
    );
  }

  async function handleDelete(postId) {
    await api.delete(`/posts/${postId}/`);
    setPosts((prev) => prev.filter((p) => p.id !== postId));
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <Navbar />
      <main className="max-w-2xl mx-auto px-4 py-8">
        {loading ? (
          <div className="flex justify-center py-20">
            <div className="w-6 h-6 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : !user ? (
          <p className="text-center text-gray-500 py-20">User not found.</p>
        ) : (
          <>
            <div className="flex items-center gap-4 mb-8">
              {user.avatar_url ? (
                <img
                  src={user.avatar_url}
                  alt={user.username}
                  className="w-16 h-16 rounded-full object-cover"
                />
              ) : (
                <div className="w-16 h-16 rounded-full bg-violet-500/20 flex items-center justify-center text-violet-400 text-2xl font-bold">
                  {user.username[0].toUpperCase()}
                </div>
              )}
              <div>
                <h1 className="text-2xl font-bold">{user.username}</h1>
                {isOwnProfile && (
                  <p className="text-sm text-gray-400">{posts.length} track{posts.length !== 1 ? "s" : ""} shared</p>
                )}
              </div>
            </div>

            {isOwnProfile ? (
              <>
                <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
                  Your history
                </h2>
                {posts.length === 0 ? (
                  <p className="text-gray-500 text-sm">You haven't shared anything yet.</p>
                ) : (
                  <div className="space-y-4">
                    {posts.map((p) => (
                      <PostCard key={p.id} post={p} onLikeToggle={handleLikeToggle} onDelete={handleDelete} />
                    ))}
                  </div>
                )}
              </>
            ) : (
              <p className="text-gray-500 text-sm">
                Post history is private — only you can see your own archive.
              </p>
            )}
          </>
        )}
      </main>
    </div>
  );
}
