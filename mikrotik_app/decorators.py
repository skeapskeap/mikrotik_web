from django.http import HttpResponse
from django.shortcuts import redirect


def is_authenticated(view):
    def wrapper(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return view(self, request, *args, **kwargs)
        else:
            return redirect('/login')
    return wrapper


def allow_access(allowed_groups={}):
    def decorator(view):

        def wrapper(self, request, *args, **kwargs):
            user_groups = set()
            if request.user.groups.exists():
                group_count = request.user.groups.all().count()                                 # Помещает все группы, к которым 
                user_groups = {request.user.groups.all()[i].name for i in range(group_count)}   # принадлежит юзер в сет

            if user_groups & allowed_groups:  # Если юзер входит хотя бы в одну из разрешенных групп
                return view(self, request, *args, **kwargs)
            else:
                return redirect('/restricted')
        return wrapper

    return decorator
