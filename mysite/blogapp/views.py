from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.syndication.views import Feed
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
)
from .models import Author, Category, Tag, Article
from .forms import AuthorForm, CategoryForm, TagForm, ArticleForm


class AuthorListView(ListView):
    template_name = "blogapp/author-list.html"
    queryset = (
        Author.objects
        .prefetch_related("articles")
    )
    context_object_name = "authors"


class AuthorCreateView(LoginRequiredMixin, CreateView):
    template_name = "blogapp/author-create.html"
    model = Author
    form_class = AuthorForm
    success_url = reverse_lazy("blogapp:authors")


class AuthorDetailView(DetailView):
    template_name = "blogapp/author-detail.html"
    model = Author
    context_object_name = "author"


class CategoryListView(ListView):
    template_name = "blogapp/category-list.html"
    queryset = (
        Category.objects
        .prefetch_related("articles")
    )
    context_object_name = "categories"


class CategoryCreateView(LoginRequiredMixin, CreateView):
    template_name = "blogapp/category-create.html"
    model = Category
    form_class = CategoryForm
    success_url = reverse_lazy("blogapp:category")


class TagListView(ListView):
    template_name = "blogapp/tag-list.html"
    queryset = (
        Tag.objects
        .prefetch_related("articles")
    )
    model = Tag
    context_object_name = "tags"


class TagCreateView(LoginRequiredMixin, CreateView):
    template_name = "blogapp/tag-create.html"
    model = Tag
    form_class = TagForm
    success_url = reverse_lazy("blogapp:tags")


class ArticleListView(ListView):
    template_name = "blogapp/article-list.html"
    queryset = (
        Article.objects
        .defer("content", "created_by")
        .select_related("author")
        .prefetch_related("category", "tags")
        .order_by("-pub_date")
    )
    context_object_name = "articles"


class LatestArticleView(Feed):
    title = "Статьи в блоге"
    description = "обновленная информация об изменениях и дополнениях в статьях блога"
    link = reverse_lazy("blogapp:articles")

    def items(self):
        return Article.objects.order_by('-pub_date')[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.content[:100] + "..."


class ArticleCreateView(LoginRequiredMixin, CreateView):
    template_name = "blogapp/article-create.html"
    model = Article
    form_class = ArticleForm
    success_url = reverse_lazy("blogapp:articles")


class ArticleDetailView(DetailView):
    template_name = "blogapp/article-detail.html"
    queryset = (
        Article.objects
        .defer("category", "tags", "created_by")
    )
    model = Article
    context_object_name = "article"


class ArticleDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "blogapp/article-delete.html"
    model = Article

    def has_permission(self):
        return self.get_object().author_id == self.request.user.pk or self.request.user.is_superuser

    def get_success_url(self):
        return reverse(
            'blogapp:articles',
        )
