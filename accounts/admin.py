from django.contrib import admin
from .models import SecurityLog, Profile, ApplicationErrorLog

admin.site.register(SecurityLog)
admin.site.register(Profile)
admin.site.register(ApplicationErrorLog)