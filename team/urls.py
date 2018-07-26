from django.urls import path

from . import views

app_name = 'team'
urlpatterns = [
    # team/  navigation page for all team stuff, user-facing
    path('', views.IndexView.as_view(), name='index'),
    # team/Cam/  user-facing individual summaries
    path('<str:player_nickname>/', views.player_view, name='player'),
    # TODO: complete PersonalInfoForm, replace here
    path('<str:player_nickname>/nickname', views.get_nickname, name='nickname'),
    # team/Cam/events  form to edit event attendance
    path('<str:player_nickname>/attendance', views.player_view, name='player_attendance'),


    # path('<slug:slug>/', views.PlayerView.as_view(), name='player'),
    # path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    # path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    # path('<int:question_id>/vote/', views.vote, name='vote'),
    ]
