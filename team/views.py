from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from .models import Player, Event, Attendance


class IndexView(generic.ListView):
    template_name = 'team/index.html'
    context_object_name = 'player_list'

    def get_queryset(self):
        return Player.objects.order_by('-gender_line')


def player_view(request, player_nickname):
    player = get_object_or_404(Player, nickname=player_nickname)  # pk=player_id)
    event_list = Event.objects.all()
    attendance = []
    for event in event_list:
        attendance.append(Attendance.objects.filter(player_id=player.id,
                                                    event_id=event.id).get().get_status_display())

    context = {'event_list': event_list,
               'player': player,
               'gender_line': player.get_gender_line_display(),
               'field_position': player.get_field_position_display(),
               'attendance': attendance,
               }

    return render(request, 'team/player.html', context)


# class PlayerView(generic.DetailView):
#     model = Player
#     template_name = 'team/player.html'
#     slug_field = 'nickname'
#
#     def show_events(self):

