from django.urls import path

from . import views

app_name = 'team'
urlpatterns = [
    # team/  navigation page for all team stuff, user-facing
    path('', views.IndexView.as_view(), name='index'),

    # team/captain/  summary of whole team attendance
    path('captain/', views.full_team_view, name='captain'),

    # team/Cam/  user-facing individual summaries
    path('<str:player_nickname>/', views.player_view, name='player'),

    # team/Cam/player_edit/  user-facing individual summaries
    path('<str:player_nickname>/player_edit/', views.player_edit_info, name='player_edit'),

    # team/Cam/attendance/EVENT  form to edit event attendance
    path('<str:player_nickname>/attendance/<str:event_name>', views.player_edit_attendance, name='player_attendance'),

    ]
