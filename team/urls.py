from django.urls import path

from . import views

app_name = 'team'
urlpatterns = [
    # team/  navigation page for all team stuff, user-facing
    path('', views.IndexView.as_view(), name='index'),

    # team/Cam/  user-facing individual summaries
    path('<str:player_nickname>/', views.player_view, name='player'),

    # team/Cam/player_edit/  user-facing individual summaries
    path('<str:player_nickname>/player_edit/', views.player_edit_info, name='player_edit'),

    # team/Cam/events  form to edit event attendance
    path('<str:player_nickname>/attendance/', views.player_edit_attendance, name='player_attendance'),

    ]
