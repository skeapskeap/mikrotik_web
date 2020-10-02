from .decorators import is_authenticated, allow_access
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.generic import View
from .forms import CheckIP, CustOperations, IPOperations
from .mikrotik import run_action


def index(request):
    if request.user.is_authenticated:
        return render(request, 'index.html')
    else:
        return redirect('/login')


def deny_access(request):
    return render(request, 'restricted.html')


class Home(View):

    @is_authenticated
    @allow_access(allowed_groups={'view_only', 'billing', 'net_admin'})
    def get(self, request):
        form = CheckIP()
        return render(request, 'home.html', {"form": form})

    def post(self, request):
        ip = request.POST.get('ip')
        reply = run_action(action='check', ip=ip)
        print(request.POST)
        return JsonResponse(reply, status=200)


class Bill(View):

    @is_authenticated
    @allow_access(allowed_groups={'billing', 'net_admin'})
    def get(self, request):
        form = IPOperations()
        return render(request, 'bill.html', {"form": form})

    def post(self, request):
        action = request.POST.get('action')
        ip = request.POST.get('ip')
        mac = request.POST.get('mac')
        reply = run_action(action=action, ip=ip, mac=mac)
        print(request.POST)
        return JsonResponse(reply, status=200)


class Config(View):

    @is_authenticated
    @allow_access(allowed_groups={'net_admin'})
    def get(self, request):
        print(request.user.user_permissions)
        form = CustOperations()
        return render(request, 'config.html', {"form": form})

    def post(self, request):
        action = request.POST.get('action')
        ip = request.POST.get('ip')
        mac = request.POST.get('mac')
        firm_name = request.POST.get('firm_name')
        url = request.POST.get('url')
        reply = run_action(action=action, ip=ip, mac=mac, firm_name=firm_name, url=url)
        print(request.POST)
        return JsonResponse(reply, status=200)
