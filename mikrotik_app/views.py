from django.shortcuts import render
from .forms import IPOperations

# Create your views here.

def index(request):
    some_variable = 'this is some variable'
    return render(request, 'index.html', locals())

def form_page(request):
    if request.method == 'POST':
        form = IPOperations(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
    else:    
        form = IPOperations()
    return render(request, 'forms.html', {"form": form})