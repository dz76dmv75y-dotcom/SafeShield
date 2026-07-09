"""
URL configuration for safe_shield project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import path, include
from django.views.generic import TemplateView
from django.utils import translation

def set_language_view(request):
    language = request.POST.get('language', '').strip()
    if language not in dict(settings.LANGUAGES):
        language = settings.LANGUAGE_CODE.split('-')[0]

    translation.activate(language)
    request.session['django_language'] = language

    response = HttpResponseRedirect(request.POST.get('next') or '/')
    response.set_cookie('django_language', language, max_age=60 * 60 * 24 * 365, path='/')
    return response


urlpatterns = [
    path('i18n/setlang/', set_language_view, name='set_language'),
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('dashboard/', include(('dashboard.urls', 'dashboard'), namespace='dashboard')),
    path('scanner/', include(('scanner.urls', 'scanner'), namespace='scanner')),
    path('protection/', include(('protection.urls', 'protection'), namespace='protection')),
    path('passwords/', include(('passwords.urls', 'passwords'), namespace='passwords')),
    path('encryption/', include(('encryption.urls', 'encryption'), namespace='encryption')),
    path('threats/', include(('threats.urls', 'threats'), namespace='threats')),
    path('reports/', include(('reports.urls', 'reports'), namespace='reports')),
    path('academy/', include(('academy.urls', 'academy'), namespace='academy')),
    path('notifications/', include(('notifications.urls', 'notifications'), namespace='notifications')),
    path('settings/', include(('settings.urls', 'settings'), namespace='settings')),
)
