from django.urls import path

from . import views

app_name = 'team'
urlpatterns = [
    # team/  navigation page for all team stuff, user-facing
    path('', views.IndexView.as_view(), name='index'),

    # team/signup  signup form
    path('signup/', views.signup, name='signup'),

    # team/captain/  summary of whole team attendance
    path('captain/', views.full_team_view, name='captain'),

    # team/player/my_info/  user-facing individual summaries
    path('player/my_info/', views.player_edit_info, name='self_edit'),

    # team/player/Cam/  user-facing individual summaries
    path('player/<str:player_nickname>/', views.player_view, name='player'),

    # team/player/Cam/player_edit/  admin-facing individual summaries
    path('player/<str:player_nickname>/player_edit/', views.player_edit_info, name='player_edit'),

    # team/player/Cam/attendance/EVENT  form to edit event attendance
    path('player/<str:player_nickname>/attendance/<str:event_name>', views.player_edit_attendance, name='player_attendance'),
    ]
