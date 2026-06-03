from django.urls import path

from .views import (
    CommentDestroyView,
    CommentLikeToggleView,
    CommentListCreateView,
    CreatePostView,
    FeedView,
    LikeToggleView,
    MyPostsView,
    PostDestroyView,
    TrackSearchView,
)

# Mounted at /api/v1/posts/
urlpatterns = [
    path("search-tracks/", TrackSearchView.as_view(), name="track_search"),
    path("", CreatePostView.as_view(), name="post_create"),
    path("feed/", FeedView.as_view(), name="post_feed"),
    path("me/", MyPostsView.as_view(), name="post_my"),
    path("<uuid:pk>/", PostDestroyView.as_view(), name="post_destroy"),
    path("<uuid:pk>/like/", LikeToggleView.as_view(), name="post_like"),
    path("<uuid:pk>/comments/", CommentListCreateView.as_view(), name="comment_list_create"),
    path("<uuid:pk>/comments/<uuid:comment_pk>/", CommentDestroyView.as_view(), name="comment_destroy"),
    path("<uuid:pk>/comments/<uuid:comment_pk>/like/", CommentLikeToggleView.as_view(), name="comment_like"),
]
