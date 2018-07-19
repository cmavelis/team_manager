from django.urls import path

from . import views

app_name = 'team'
urlpatterns = [
    # team/
    path('', views.IndexView.as_view(), name='index'),
    # team/3/
    path('<str:player_nickname>/', views.player_view, name='player'),
    # path('<slug:slug>/', views.PlayerView.as_view(), name='player'),
    # path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    # path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    # path('<int:question_id>/vote/', views.vote, name='vote'),
    ]
