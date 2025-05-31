from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    DeleteView,
    UpdateView,
)
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.core.paginator import Paginator
from django.db.models import Count

from .models import Post, Category, Comment
from .forms import PostForm, CommentCreateForm


def get_queryset_with_comment_counts(posts):
    return posts.annotate(comment_count=Count("comment"))


def paginate_items(queryset, request, per_page=10):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


class BaseCommentMixin:
    model = Comment
    form_class = CommentCreateForm
    template_name = "blog/comment.html"

    def get_post(self):
        return get_object_or_404(Post, id=self.kwargs["post"])

    def get_success_url(self):
        return reverse_lazy(
            "blog:post_detail",
            kwargs={
                "post": self.get_post().id,
            },
        )


class AuthorCheckCommentMixin(BaseCommentMixin):
    def get_object(self, queryset=None):
        comment = get_object_or_404(Comment, pk=self.kwargs["comment"])
        post = get_object_or_404(Post, pk=self.kwargs["post"])
        if comment.author != self.request.user or comment.post != post:
            raise Http404("Запрещено")
        return comment


class PostQuerySetMixin:
    model = Post
    paginate_by = 10

    def get_queryset(self):
        now = timezone.now()
        posts = Post.objects.filter(
            pub_date__lte=now,
            is_published=True,
            category__is_published=True,
        )
        return get_queryset_with_comment_counts(posts).order_by("-pub_date")


class CommentCreateView(LoginRequiredMixin, BaseCommentMixin, CreateView):
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.get_post()
        return super().form_valid(form)


class CommentEditView(LoginRequiredMixin, AuthorCheckCommentMixin, UpdateView):
    model = Comment
    form_class = CommentCreateForm
    template_name = "blog/comment.html"

    def get_success_url(self):
        return reverse_lazy(
            "blog:post_detail",
            kwargs={
                "post": self.object.post.id,
            },
        )


class CommentRemoveView(LoginRequiredMixin, AuthorCheckCommentMixin, DeleteView):
    model = Comment
    template_name = "blog/comment.html"

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment'] = self.get_object()
        # Удаляем ключ 'form', если он присутствует
        context.pop('form', None)
        return context

    def get_success_url(self):
        return reverse_lazy(
            "blog:post_detail",
            kwargs={
                "post": self.object.post.id,
            },
        )


class UserProfileView(DetailView):
    model = get_user_model()
    template_name = "blog/profile.html"
    context_object_name = "profile"

    def get_object(self, queryset=None):
        return get_object_or_404(
            get_user_model(),
            username=self.kwargs["username"],
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        if self.request.user == self.object:
            posts = Post.objects.filter(author=self.object)
        else:
            posts = Post.objects.filter(
                author=self.object,
                is_published=True,
                pub_date__lte=now,
                category__is_published=True,
            )
        posts = get_queryset_with_comment_counts(posts).order_by("-pub_date")
        context["page_obj"] = paginate_items(posts, self.request)
        return context


class UserEditView(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    template_name = "blog/user.html"
    context_object_name = "profile"
    fields = ["username", "first_name", "last_name", "email"]

    def get_object(self, queryset=None):
        return self.request.user


    def get_success_url(self):
        return reverse_lazy(
            "blog:profile",
            kwargs={
                "username": self.object.username,
            },
        )


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/create.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "blog:profile",
            kwargs={
                "username": self.request.user.username,
            },
        )


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog/create.html"
    pk_url_kwarg = "post"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(
                "blog:post_detail",
                post=self.kwargs["post"],
            )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        if form.instance.author != self.request.user:
            return redirect(
                "blog:post_detail",
                post=self.kwargs["post"],
            )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "blog:profile",
            kwargs={
                "username": self.request.user.username,
            },
        )


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = "blog/create.html"

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, pk=self.kwargs["post"])
        if post.author != self.request.user and not self.request.user.is_staff:
            raise Http404("Удаление запрещено")
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = PostForm(instance=self.get_object())
        return context

    def get_success_url(self):
        return reverse(
            "blog:profile",
            kwargs={
                "username": self.request.user.username,
            },
        )


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/detail.html"
    context_object_name = "post"

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, pk=self.kwargs["post"])
        now = timezone.now()
        if self.request.user != post.author:
            if post.pub_date > now or not post.is_published:
                raise Http404("Публикация не найдена или недоступна.")
            if not post.category.is_published:
                raise Http404("Категория недоступна.")
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comments"] = self.object.comment_set.all().order_by("created_at")
        if self.request.user.is_authenticated:
            context["form"] = CommentCreateForm()
        return context


class PostsListView(PostQuerySetMixin, ListView):
    template_name = "blog/index.html"


class CategoryListView(PostQuerySetMixin, ListView):
    template_name = "blog/category.html"
    context_object_name = "page_obj"

    def get_queryset(self):
        category = get_object_or_404(
            Category,
            slug=self.kwargs["slug"],
            is_published=True,
        )
        return get_queryset_with_comment_counts(
            super().get_queryset().filter(category=category)
        ).order_by("-pub_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = get_object_or_404(
            Category,
            slug=self.kwargs["slug"],
            is_published=True,
        )
        return context
