from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.views.decorators.cache import cache_page

from posts.models import Post, Group, User, Follow
from posts.forms import PostForm, CommentForm


@cache_page(20)
def index(request):
    posts = Post.objects.order_by('-pub_date')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by('-pub_date')
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=author).all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    count_post = post_list.count()
    follower = Follow.objects.filter(user=author)
    following = Follow.objects.filter(author=author)
    context = {
        'profile': author,
        'page_obj': page_obj,
        'paginator': paginator,
        'count_post': count_post,
        'follower': follower,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    author = post.author
    post_list = Post.objects.filter(author=author).all()
    count_post = post_list.count()
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        'post': post,
        'count_post': count_post,
        'comments': comments,
        'form': form
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    groups = Group.objects.all()
    form = PostForm(request.POST or None, files=request.FILES or None)
    context = {
        'groups': groups,
        'form': form
    }
    if not form.is_valid():
        return render(request, 'posts/create_post.html', context)
    new_post = form.save(commit=False)
    new_post.author = request.user
    form.save()
    return redirect('posts:profile', username=new_post.author)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    groups = Group.objects.all()
    is_edit = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=is_edit
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'form': form,
        'is_edit': is_edit,
        'groups': groups,
        'post': post,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'profile': profile,
        'post': post,
        'comments': comments,
        'form': form
    }
    return render(request, 'posts/comments.html', context)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    follower = request.user
    following = get_object_or_404(User, username=username)
    if following == request.user:
        return redirect('posts:profile', username=username)
    author_list, created = Follow.objects.get_or_create(
        user=follower,
        author=following
    )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    follower = request.user
    following = get_object_or_404(User, username=username)
    author_list = Follow.objects.filter(user=follower, author=following)
    if not username == follower.username and author_list:
        author_list.delete()
    return redirect('posts:profile', username=username)
