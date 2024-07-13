from django.urls import path
from .views import (
    AuthorListView,
    AuthorCreateView,
    AuthorDetailView,

    CategoryListView,
    CategoryCreateView,

    TagListView,
    TagCreateView,

    ArticleListView,
    LatestArticleView,
    ArticleCreateView,
    ArticleDetailView,
    ArticleDeleteView,
)

app_name = "blogapp"


urlpatterns = [
    path("authors/", AuthorListView.as_view(), name="authors"),
    path("authors/create/", AuthorCreateView.as_view(), name="create_author"),
    path("authors/<int:pk>/", AuthorDetailView.as_view(), name="author_detail"),


    path("category/", CategoryListView.as_view(), name="category"),
    path("category/create/", CategoryCreateView.as_view(), name="category_create"),

    path("tags/", TagListView.as_view(), name="tags"),
    path("tags/create/", TagCreateView.as_view(), name="create_tag"),


    path("articles/", ArticleListView.as_view(), name="articles"),
    path("articles/latest/feed", LatestArticleView(), name="latest_articles"),
    path("articles/<int:pk>/", ArticleDetailView.as_view(), name="article_detail"),
    path("articles/create/", ArticleCreateView.as_view(), name="create_article"),
    path("articles/<int:pk>/delete/", ArticleDeleteView.as_view(), name="delete_article"),
]
