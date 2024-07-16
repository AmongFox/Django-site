from random import random

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.cache import cache_page
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import ProfileEditForm
from .models import Profile


class ProfileView(DetailView):
    """
    Вывод данных о пользователе
    template_name: String - Шаблон отрисовки HTML кода
    """
    template_name = "myauth/profile.html"
    context_object_name = "user"
    model = User

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["myuser"] = self.request.user
        return context


class ProfileListView(ListView):
    template_name = "myauth/profile-list.html"
    context_object_name = "users"
    model = User
    queryset = (
        User.objects.all()
        .select_related("profile_user").only("profile_user", "username")
    )

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["myuser_id"] = self.request.user.pk
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    template_name = "myauth/profile-edit.html"
    model = User
    form_class = ProfileEditForm

    def has_permission(self):
        if self.kwargs.get("pk") == self.request.user.pk or self.request.user.is_superuser:
            return True

    def get_success_url(self):
        return reverse(
            'myauth:profile', kwargs={"pk": self.kwargs.get("pk")},
        )


class RegisterView(CreateView):
    """
    Регистрация нового пользователя
    form_class: Class - Модель заполнения данных в форме
    template_name: String - Шаблон отрисовки HTML кода
    success_url: String - Ссылка для перехода после регистрации
    """
    form_class = UserCreationForm
    template_name = "myauth/register.html"

    def form_valid(self, form) -> HttpResponse:
        response = super().form_valid(form)
        Profile.objects.create(user=self.object)

        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")

        user = authenticate(
            self.request,
            username=username,
            password=password,
        )
        login(request=self.request, user=user)
        return response

    def get_success_url(self):
        return reverse(
            'myauth:profile_list',
        )


def logout_view(request: HttpRequest):
    logout(request)
    return redirect(reverse("myauth:login"))


def set_cookie_view() -> HttpResponse:
    response = HttpResponse()
    response.set_cookie("my_cookie", "my_value", max_age=3600)
    return response


@cache_page(120)
def get_cookie_view(request: HttpRequest) -> HttpResponse:
    cookie = request.COOKIES.get("my_cookie", "default value")
    return HttpResponse(f"Cookie: {cookie!r} + {random()}")


@permission_required("myauth.view_profile", raise_exception=True)
def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session["my_session"] = "my_value"
    return HttpResponse("Session set")


def get_session_view(request: HttpRequest) -> HttpResponse:
    session = request.session.get("my_session", "default value")
    return HttpResponse(f"Session: {session!r}")
