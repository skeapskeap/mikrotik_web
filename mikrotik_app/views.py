from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import View
from .forms import CustOperations, IPOperations
from .mikrotik import run_action


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
        mac = request.POST.get('mac')
        reply = run_action(action, ip=ip, mac=mac)
        print(request.POST)
        return JsonResponse(reply, status=200)


class custForm(View):
    def get(self, request):
        print(request.user.user_permissions)
        form = CustOperations()
        return render(request, 'customers.html', {"form": form})

    def post(self, request):
        action = request.POST.get('action')
        ip = request.POST.get('ip')
        mac = request.POST.get('mac')
        firm_name = request.POST.get('firm_name')
        url = request.POST.get('url')
        reply = run_action(action, ip=ip, mac=mac, firm_name=firm_name, url=url)
        print(request.POST)
        return JsonResponse(reply, status=200)
