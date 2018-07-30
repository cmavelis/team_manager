from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from .models import Player, Event, Attendance
from .forms import PlayerForm


class IndexView(generic.ListView):
    # list of all Players, with hyperlinks to their personal pages
    template_name = 'team/index.html'
    context_object_name = 'player_list'

    def get_queryset(self):
        return Player.objects.order_by('-gender_line')


def player_view(request, player_nickname):
    # relevant information for each Player to see on their page, leading to forms
    player = get_object_or_404(Player, nickname=player_nickname)  # pk=player_id)
    # all Events
    event_list = Event.objects.all()
    # Player's attendance, by Event
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


def get_nickname(request, player_nickname):
    # if this is a POST request we need to process the form data
    player = get_object_or_404(Player, nickname=player_nickname)
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = PlayerForm(request.POST, instance=player)

        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            form.save()
            # redirect to a new URL:
            return HttpResponseRedirect('/thanks/')
    # if a GET (or any other method) we'll create a blank form
    else:
        form = PlayerForm(instance=player)

    return render(request, 'nickname.html', {'form': form})

# def player_event_edit(request, player_nickname):

    # wait, should this just also use player_view, but a different template?
    # don't know how to do this, unless subclassing
    # This should probably be a form


# class PlayerView(generic.DetailView):
#     model = Player
#     template_name = 'team/player.html'
#     slug_field = 'nickname'
#
#     def show_events(self):

