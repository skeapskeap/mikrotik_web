from django.urls import path
from . import views


urlpatterns = [
    path('', views.Home.as_view(), name='homepage'),
    path('restricted/', views.deny_access, name='restricted'),
    path('bill/', views.Bill.as_view(), name='bill'),
    path('config/', views.Config.as_view(), name='config'),
]
