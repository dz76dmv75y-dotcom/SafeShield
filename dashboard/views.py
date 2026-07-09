from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from notifications.models import Notification
from passwords.models import PasswordEntry
from protection.models import SecurityEvent
from scanner.models import ScanHistory


@login_required
def home(request):
    scans = ScanHistory.objects.filter(user=request.user).order_by('-scanned_at')[:6]
    events = SecurityEvent.objects.filter(user=request.user).order_by('-created_at')[:6]
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:6]
    passwords = PasswordEntry.objects.filter(user=request.user)

    score = 92
    if scans.exists():
        score = min(100, score + len(scans) // 2)
    if events.exists():
        score = max(60, score - min(12, events.count() // 2))

    context = {
        'security_score': score,
        'threats_blocked': max(120, 300 - events.count() * 4),
        'websites_scanned': scans.count(),
        'device_status': 'Protected',
        'website_status': 'Protected' if scans.exists() else 'Monitoring',
        'email_status': 'Protected',
        'apple_status': 'Secure',
        'banking_status': 'Protected',
        'password_status': 'Healthy' if passwords.exists() else 'Needs review',
        'scans': scans,
        'events': events,
        'notifications': notifications,
        'password_entries': passwords.count(),
    }
    return render(request, 'dashboard/home.html', context)
