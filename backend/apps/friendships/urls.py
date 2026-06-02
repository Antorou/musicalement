from django.urls import path

from .views import FriendshipDetailView, FriendshipListCreateView

# Mounted at /api/v1/friendships/
urlpatterns = [
    path("", FriendshipListCreateView.as_view(), name="friendship_list_create"),
    path("<int:pk>/", FriendshipDetailView.as_view(), name="friendship_detail"),
]
