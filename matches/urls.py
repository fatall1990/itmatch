from django.urls import path
from . import views

app_name = 'matches'

urlpatterns = [
    path('', views.user_feed, name='feed'),
    path('matches/', views.matches_list, name='matches_list'),
    path('matches/<int:match_id>/', views.match_detail, name='match_detail'),
    path('like/<int:user_id>/', views.send_like, name='send_like'),
    path('dislike/<int:user_id>/', views.send_dislike, name='send_dislike'),
path('debug/', views.debug_info, name='debug_info'),
]