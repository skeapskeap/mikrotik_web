from django.shortcuts import render

# Create your views here.

def index(request):
    some_variable = 'this is some variable'
    return render(request, 'index.html', locals())