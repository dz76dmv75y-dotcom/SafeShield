from django.urls import path

from . import views

urlpatterns = [
    path('', views.accounts_view, name='accounts'),
    path('events/', views.events_view, name='events'),
    path('simulate/', views.simulate_protection, name='simulate'),
    path('banking/', views.banking_security, name='banking'),
]
