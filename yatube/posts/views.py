from django.shortcuts import render, get_object_or_404, get_list_or_404
from .models import Post, Group, User, Follow
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect
from .forms import PostForm, CommentForm
from django.views.decorators.cache import cache_page

NUMBER_OF_POSTS_PER_PAGE = 10


def paginator_page(request, posts):
    page_number = request.GET.get('page')
    paginator = Paginator(posts, NUMBER_OF_POSTS_PER_PAGE)
    return paginator.get_page(page_number)


def index(request):
    template = 'posts/index.html'
    posts = Post.objects.select_related('author', 'group')
    page_obj = paginator_page(request, posts)
    context = {'posts': posts,
               'page_obj': page_obj}
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author', 'group')
    page_obj = paginator_page(request, posts)
    context = {'group': group,
               'posts': posts,
               'page_obj': page_obj}
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    page_obj = paginator_page(request, posts)
    context = {'posts': posts,
               'author': author,
               'page_obj': page_obj}
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    comments = post.comments.select_related('author')
    context = {'post': post,
               'comments': comments,
               'form': form}
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None, files=request.FILES or None)
    context = {'form': form}
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user)
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post_id)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {'form': form,
               'post': post,
               'is_edit': True}
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)

@login_required
def follow_index(request):
    # информация о текущем пользователе доступна в переменной request.user
    user = request.user
    authors = get_list_or_404(Follow, user=user)
    posts = []
    for author in authors:
        posts += author.posts.all()
    context = {'posts': posts}
    return render(request, 'posts/follow.html', context)

