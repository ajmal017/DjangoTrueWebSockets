from django.db import models
from rest_framework.serializers import ModelSerializer


class Post(models.Model):
    text = models.TextField()

    def __str__(self):
        return f'Post {self.text}'


class PostSerializer(ModelSerializer):
    class Meta:
        model = Post
        fields = ('pk', 'text')
        