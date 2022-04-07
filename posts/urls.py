from django.urls import path
from posts import views

app_name = 'posts'

urlpatterns = [
    path('', views.index, name='posts_list'),
    path('group/<slug:slug>/', views.group_posts, name='group_list'),
]
