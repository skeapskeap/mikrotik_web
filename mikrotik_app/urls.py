from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('restricted/', views.deny_access, name='restricted'),
    path('form/', views.indexForm.as_view(), name='form'),
    path('customers/', views.custForm.as_view(), name='customers'),
]
