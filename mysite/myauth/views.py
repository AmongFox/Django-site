from random import random

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy, ngettext
from django.views.decorators.cache import cache_page
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
    View
)

from .forms import ProfileEditForm
from .models import Profile


class HelloView(View):
    welcome_msg = gettext_lazy("Hello world!")

    def get(self, request: HttpRequest) -> HttpResponse:
        items_str = request.GET.get('items') or 0
        items = int(items_str)
        products_line = ngettext(
            "one product",
            "{count} products",
            items,
        )
        products_line = products_line.format(count=items)
        return HttpResponse(
            f"<h1>{self.welcome_msg}</h1>"
            f"\n<h2>{products_line}</h2>"
        )


class ProfileView(DetailView):
    """
    Вывод данных о пользователе
    template_name: String - Шаблон отрисовки HTML кода
    """
    queryset = Profile.objects.prefetch_related("user")
    template_name = "myauth/profile.html"
    context_object_name = "profile"


class ProfileListView(ListView):
    template_name = "myauth/profile-list.html"
    queryset = Profile.objects.all()
    context_object_name = "profiles"


class ProfileEditView(LoginRequiredMixin, UpdateView):
    template_name = "myauth/profile-edit.html"
    model = Profile
    form_class = ProfileEditForm

    def has_permission(self):
        if self.get_object().user_id == self.request.user.pk or self.request.user.is_superuser:
            return True

    def get_success_url(self):
        return reverse(
            'myauth:profile', kwargs={"pk": self.object.pk},
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
    success_url = reverse_lazy("myauth:profile")

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


def logout_view(request: HttpRequest):
    logout(request)
    return redirect(reverse("myauth:login"))


def set_cookie_view(request: HttpRequest):
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
