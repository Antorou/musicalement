from django.urls import path

from .views import (
    BlockDestroyView,
    BlockListCreateView,
    FriendshipDetailView,
    FriendshipListCreateView,
)

# Mounted at /api/v1/friendships/
urlpatterns = [
    path("", FriendshipListCreateView.as_view(), name="friendship_list_create"),
    path("blocks/", BlockListCreateView.as_view(), name="block_list_create"),
    path("blocks/<int:pk>/", BlockDestroyView.as_view(), name="block_destroy"),
    path("<int:pk>/", FriendshipDetailView.as_view(), name="friendship_detail"),
]
