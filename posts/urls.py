from django.urls import path
from posts import views

urlpatterns = [
    # Главная страница
    path('', views.index),
    # Страница с постами
    path('groups/<slug:slug>/', views.group_posts),
    #path('posts/', views.posts),
    # Отдельная страница с информацией о сорте мороженого
    #path('posts/<int:pk>/', views.posts),
]