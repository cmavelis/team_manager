from django.urls import path

from . import views

app_name = 'team'
urlpatterns = [
    # team/  navigation page for all team stuff, user-facing
    path('', views.IndexView.as_view(), name='index'),

    # team/signup  signup form
    path('signup/', views.signup, name='signup'),

    # team/player/Cam/  user-facing individual summaries
    path('player/<str:player_nickname>/', views.player_view, name='player'),

    # team/player/Cam/player_edit/  user-facing individual summaries
    path('player/<str:player_nickname>/player_edit/', views.player_edit_info, name='player_edit'),

    # team/player/Cam/events  form to edit event attendance
    path('player/<str:player_nickname>/attendance/', views.player_edit_attendance, name='player_attendance'),

    ]
