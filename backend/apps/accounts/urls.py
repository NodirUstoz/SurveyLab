from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("change-password/", views.ChangePasswordView.as_view(), name="change_password"),
    path("organization/", views.OrganizationView.as_view(), name="organization"),
    path(
        "organization/members/",
        views.OrganizationMembersView.as_view(),
        name="organization_members",
    ),
]
