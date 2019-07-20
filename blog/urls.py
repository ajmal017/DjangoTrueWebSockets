from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('post', views.PostViewSet)

urlpatterns = [
    path('', views.index_view),
    path('posts/', views.post_view),
]

urlpatterns += router.urls
