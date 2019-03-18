from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from .models import Player, Event, Attendance
from .forms import PlayerForm, AttendanceForm


class IndexView(generic.ListView):
    # list of all Players, with hyperlinks to their personal pages
    template_name = 'team/index.html'
    context_object_name = 'player_list'

    def get_queryset(self):
        return Player.objects.order_by('-gender_line')


def player_view(request, player_nickname):
    # relevant information for each Player to see on their page, leading to forms
    player = get_object_or_404(Player, nickname=player_nickname)  # pk=player_id)
    # # all Events
    # event_list = Event.objects.all()
    # Player's attendance, by Event
    attendance_objects = player.attendance_set.all()
    event_list = []
    status_list = []
    pair_list = []
    for att in attendance_objects:
        event_list.append(att.event)
        status_list.append(att.status)
        pair_list.append([att.event, att.status])
    # for event in event_list:
    #     try:
    #         event_attendance = Attendance.objects.filter(player_id=player.id,
    #                                                      event_id=event.id).get().get_status_display()
    #     except Attendance.DoesNotExist:
    #         raise Http404("Attendance object does not exist")
    #     attendance.append(event_attendance)

    context = {'event_list': event_list,
               'player': player,
               'gender_line': player.get_gender_line_display(),
               'field_position': player.get_field_position_display(),
               'attendance': status_list,
               'pairs': pair_list,
               }

    return render(request, 'team/player.html', context)


def player_edit_info(request, player_nickname):
    # if this is a POST request we need to process the form data
    player = get_object_or_404(Player, nickname=player_nickname)
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = PlayerForm(request.POST, instance=player)

        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            form.save()
            # redirect to a new URL
            return HttpResponseRedirect(reverse('team:player', kwargs={'player_nickname': player_nickname}))
    # if a GET (or any other method) we'll create a blank form
    else:
        form = PlayerForm(instance=player)

    return render(request, 'team/player_info_form.html', {'form': form})


def player_edit_attendance(request, player_nickname, event_name):
    # if this is a POST request we need to process the form data
    player = Player.objects.filter(nickname=player_nickname).get()
    event = Event.objects.filter(name=event_name).get()
    attendance = get_object_or_404(Attendance, event_id=event.id, player_id=player.id)

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = AttendanceForm(request.POST, instance=attendance)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            form.save()
            # redirect to a new URL:
            return HttpResponseRedirect(reverse('team:player', kwargs={'player_nickname': player_nickname}))
    # if a GET (or any other method) we'll create a blank form
    else:
        form = AttendanceForm()

    return render(request, 'team/attendance_form.html', {'form': form})


def full_team_view(request):
    # all Events, in order of date
    event_list = Event.objects.all().order_by('date')
    # Player's attendance, by Event
    players_info = []
    for player in Player.objects.all():
        new_entry = [player.nickname]
        attendance = player.attendance_set.all()
        for event in event_list:
            try:
                new_entry.append(attendance.get(event=event.id).status)
            except Attendance.DoesNotExist:
                new_entry.append('ERR')
        players_info.append(new_entry)

    context = {'event_list': event_list,
               'players_info': players_info,
               }

    return render(request, 'team/captain_summary.html', context)

# class PlayerView(generic.DetailView):
#     model = Player
#     template_name = 'team/player.html'
#     slug_field = 'nickname'
#
#     def show_events(self):

