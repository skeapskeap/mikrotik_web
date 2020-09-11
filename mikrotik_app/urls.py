from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('form/', views.form_page, name='form'),
    path('process/', views.process, name='process'),
]
