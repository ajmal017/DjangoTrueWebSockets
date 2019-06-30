from django.shortcuts import render, redirect
from .forms import PostForm
from .models import Post
import redis


def post_view(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            instance: Post = form.save()
            red = redis.Redis()
            red.publish('new_post', str(instance))
            return redirect('/posts')
    else:
        form = PostForm()

    posts = Post.objects.all()
    return render(request, 'blog/posts.html', {'form': form, 'posts': posts})


def index_view(request):
    return render(request, 'blog/index.html')
