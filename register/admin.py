from django.contrib import admin
from django.contrib.auth.models import Group

default_groups = ['billing', 'view_only', 'net_admin']
for group in default_groups:
    Group.objects.update_or_create(name=group)