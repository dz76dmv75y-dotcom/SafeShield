from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('text/encrypt/', views.encrypt_text, name='encrypt_text'),
    path('text/decrypt/', views.decrypt_text, name='decrypt_text'),
    path('file/encrypt/', views.encrypt_file, name='encrypt_file'),
    path('file/decrypt/', views.decrypt_file, name='decrypt_file'),
]
