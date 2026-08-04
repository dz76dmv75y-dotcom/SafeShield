from django.urls import path
from . import views

app_name = "protection"

urlpatterns = [

    path('', views.accounts_view, name='accounts'),

    path('events/', views.events_view, name='events'),

    path('simulate/', views.simulate_protection, name='simulate'),

    path('banking/', views.banking_security, name='banking'),

    path('scanner/', views.link_scanner, name='link_scanner'),

    path('encrypt/', views.file_encrypt, name='file_encrypt'),

    path('phishing/', views.phishing_detector, name='phishing_detector'),

    path('malware/', views.malware_scan, name='malware_scan'),

    path('center/', views.security_center, name='security_center'),

]