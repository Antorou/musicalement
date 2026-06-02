from django.urls import path

from .views import MeView, UserDetailView, UserSearchView

# Mounted at /api/v1/users/
urlpatterns = [
    path("me/", MeView.as_view(), name="user_me"),
    path("", UserSearchView.as_view(), name="user_search"),
    path("<uuid:pk>/", UserDetailView.as_view(), name="user_detail"),
]
