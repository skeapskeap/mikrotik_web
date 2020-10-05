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
        form = CheckIP(request.POST or None)
        if form.is_valid():
            ip = request.POST.get('ip')
            reply = run_action(action='check', ip=ip)
        else:
            '''
            working code for multiple errors
                keys = form.errors.keys()
                errors = [dict(form.errors.items()).get(key) for key in keys]
            '''
            error = dict(form.errors.items()).get('ip')
            reply = {'error': error}
        return JsonResponse(reply, status=200)


class Bill(View):

    @is_authenticated
    @allow_access(allowed_groups={'billing', 'net_admin'})
    def get(self, request):
        form = IPOperations()
        return render(request, 'bill.html', {"form": form})

    def post(self, request):
        form = IPOperations(request.POST or None)
        if form.is_valid():
            print(request.POST)
            action = request.POST.get('action')
            ip = request.POST.get('ip')
            reply = run_action(action=action, ip=ip)
        else:
            error = dict(form.errors.items()).get('ip')
            reply = {'error': error}
        return JsonResponse(reply, status=200)


class Config(View):

    @is_authenticated
    @allow_access(allowed_groups={'net_admin'})
    def get(self, request):
        print(request.user.user_permissions)
        form = CustOperations()
        return render(request, 'config.html', {"form": form})

    def post(self, request):
        form = CustOperations(request.POST or None)
        print(request.POST)
        if form.is_valid():
            action = request.POST.get('action')
            ip = request.POST.get('ip')
            mac = request.POST.get('mac')
            firm_name = request.POST.get('firm_name')
            url = request.POST.get('url')
            reply = run_action(action=action, ip=ip, mac=mac, firm_name=firm_name, url=url)
        else:
            for _ in form.errors.items():
                print(f'errors = {_}')
            error = dict(form.errors.items())
            reply = {'error': error}
        return JsonResponse(reply, status=200)
