from .decorators import is_authenticated, allow_access
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.generic import View
from .forms import BillForm, ConfigForm, HomeForm
from .mikrotik import run_action
from .utils import write_log


def deny_access(request):
    return render(request, 'restricted.html')


class Home(View):

    @is_authenticated
    @allow_access(allowed_groups={'view_only', 'billing', 'net_admin'})
    def get(self, request):
        form = HomeForm()
        return render(request, 'home.html', {"form": form})

    def post(self, request):
        form = HomeForm(request.POST or None)
        if form.is_valid():
            ip = request.POST.get('ip')
            write_log(request)
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
        form = BillForm()
        return render(request, 'bill.html', {"form": form})

    def post(self, request):
        form = BillForm(request.POST or None)
        if form.is_valid():
            action  = request.POST.get('action')
            ip      = request.POST.get('ip').strip()
            write_log(request)
            reply = run_action(action=action, ip=ip)
        else:
            error = dict(form.errors.items()).get('ip')
            reply = {'error': error}
        return JsonResponse(reply, status=200)


class Config(View):

    @is_authenticated
    @allow_access(allowed_groups={'net_admin'})
    def get(self, request):
        form = ConfigForm()
        return render(request, 'config.html', {"form": form})

    def post(self, request):
        form = ConfigForm(request.POST or None)
        if form.is_valid():
            action      = request.POST.get('action')
            ip          = request.POST.get('ip').strip()
            mac         = form.cleaned_data.get('mac')  # in clean method mac converts to a proper mikrotik form
            firm_name   = request.POST.get('firm_name')
            url         = request.POST.get('url')
            write_log(request)
            reply = run_action(action=action, ip=ip, mac=mac, firm_name=firm_name, url=url)
        else:
            error = dict(form.errors.items())
            reply = {'error': error}
        return JsonResponse(reply, status=200)
