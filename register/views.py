from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from mikrotik_app.decorators import not_authenticated
from .forms import RegisterForm

@not_authenticated
def register(response):
    if response.method == 'POST':
        form = RegisterForm(response.POST)
        if form.is_valid():
            user = form.save()  # сохраняет нового пользователя в БД
            default_group = Group.objects.get(name='view_only')  # получает объект группы по названию view_only
            user.groups.add(default_group)  # добавляет новому пользователю группу по умолчанию
            return redirect('/')
        else:
            return render(response, "register/register.html", {'form': form})
    else:
        form = RegisterForm()

    return render(response, "register/register.html", {'form': form})
