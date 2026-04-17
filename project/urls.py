from django.contrib import admin
from django.urls import include, path

from voting_system import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/posts/", views.PostList.as_view(), name="post-list"),
    path("api/posts/<int:pk>/", views.PostRetrieveDestroy.as_view(), name="post-detail"),
    path("api/posts/<int:pk>/vote/", views.VoteCreate.as_view(), name="post-vote"),
    path("api/signup/", views.SignupView.as_view(), name="signup"),
    path("api/login/", views.LoginView.as_view(), name="login"),
    path("api-auth/", include("rest_framework.urls")),
]
