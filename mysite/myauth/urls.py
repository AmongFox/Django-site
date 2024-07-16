from django.contrib.auth.views import LoginView
from django.urls import path
from django.views.decorators.cache import cache_page

from .views import (
    ProfileEditView,
    ProfileListView,
    ProfileView,
    RegisterView,
    get_cookie_view,
    get_session_view,
    logout_view,
    set_cookie_view,
    set_session_view,
)

app_name = "myauth"


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(
        template_name="myauth/login.html",
        redirect_authenticated_user=True,
    ),
        name="login"
        ),
    path("logout/", logout_view, name="logout"),

    path("profile/<int:pk>/", ProfileView.as_view(), name="profile"),
    path("profile/list/", cache_page(60)(ProfileListView.as_view()), name="profile_list"),
    path("profile/<int:pk>/edit/", ProfileEditView.as_view(), name="profile_edit"),

    path("cookie/get/", get_cookie_view, name="cookie_get"),
    path("cookie/set/", set_cookie_view, name="cookie_set"),

    path("session/get/", get_session_view, name="session_get"),
    path("session/set/", set_session_view, name="session_set"),
]
