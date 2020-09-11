from django.shortcuts import render
from .forms import IPOperations
from .mikrotik import output

# Create your views here.


def index(request):
    some_variable = 'this is some variable'
    return render(request, 'index.html', locals())


def form_page(request):
    form = IPOperations()
    return render(request, 'forms.html', {"form": form})


def process(request):
    form = IPOperations(request.POST)
    if form.is_valid():
        ip = form.cleaned_data.get('ip')
        action = form.cleaned_data.get('action')
        #do_actions(ip, action)
        title = 'Я проверил'
        return render(request, 'result.html', {'output': output(ip, action), 'title': title})
    else:
        form = IPOperations()
        return render(request, 'forms.html', {"form": form})
