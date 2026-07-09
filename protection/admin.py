from django.contrib import admin

from .models import ProtectedAccount, SecurityEvent


@admin.register(ProtectedAccount)
class ProtectedAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'account_type', 'name', 'status', 'last_checked')
    list_filter = ('account_type', 'status')
    search_fields = ('name', 'username', 'user__username')


@admin.register(SecurityEvent)
class SecurityEventAdmin(admin.ModelAdmin):
    list_display = ('user', 'event_type', 'title', 'severity', 'created_at', 'is_resolved')
    list_filter = ('event_type', 'severity', 'is_resolved')
    search_fields = ('title', 'details', 'user__username')
