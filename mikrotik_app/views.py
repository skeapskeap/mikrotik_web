from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import View
from .forms import IPOperations
from .mikrotik import output


def index(request):
    some_variable = 'this is some variable'
    return render(request, 'index.html', locals())


class indexForm(View):
    def get(self, request):
        form = IPOperations()
        return render(request, 'forms.html', {"form": form})

    def post(self, request):
        action = request.POST.get('action')
        ip = request.POST.get('ip')
        reply = output(ip, action)
        print(request.POST)
        return JsonResponse(reply, status=200)
