from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse


@csrf_exempt
def slack_test(request):
    if request.method == 'POST':
        payload = request.POST
    else:
        return Http404
    print(payload)
    if payload['command'] == '/test_hi':
        response = {
            'text': 'Hi',
            'attachments': [
                {
                    'text': 'Sent by {}'.format(payload['user_name'])
                }
            ]
        }

        return JsonResponse(response)
