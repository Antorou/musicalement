from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("apps.users.urls")),
    path("api/v1/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/v1/users/", include("apps.users.urls_users")),
    path("api/v1/posts/", include("apps.posts.urls")),
    path("api/v1/friendships/", include("apps.friendships.urls")),
]
