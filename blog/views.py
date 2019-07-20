from django.shortcuts import render, redirect
from .forms import PostForm
from .models import Post, PostSerializer
from rest_framework.viewsets import ModelViewSet
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


class PostViewSet(ModelViewSet):
    serializer_class = PostSerializer
    queryset = Post.objects.all()


def index_view(request):
    return render(request, 'blog/index.html')
