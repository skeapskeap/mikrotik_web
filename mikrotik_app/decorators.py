from django.shortcuts import redirect
from .utils import mikrotik


def is_authenticated(view):
    def wrapper(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return view(self, request, *args, **kwargs)
        else:
            return redirect('/login')
    return wrapper


def not_authenticated(func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/')
        else:
            return func(request, *args, **kwargs)
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


def unique_mac(func):
    def wrapper(**kwargs):
        arp_print = '/ip/arp/print'
        dhcp_print = '/ip/dhcp-server/lease/print'
        options = {'mac-address': kwargs.get('mac'), 'dynamic': 'false'}

        arp_overlap = mikrotik().query(arp_print).equal(**options)
        dhcp_overlap = mikrotik().query(dhcp_print).equal(**options)

        if arp_overlap or dhcp_overlap:
            return {'message': ['Такой MAC уже существует', ['Увы :E']]}
        else:
            return func(**kwargs)
    return wrapper
