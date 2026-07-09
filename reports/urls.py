from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('export-pdf/', views.export_pdf, name='export_pdf'),
]
