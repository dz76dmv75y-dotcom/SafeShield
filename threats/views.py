from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from protection.models import SecurityEvent
from scanner.models import ScanHistory

from .models import ThreatAlert


@login_required
def home(request):
    events = SecurityEvent.objects.filter(user=request.user).order_by('-created_at')[:10]
    scans = ScanHistory.objects.filter(user=request.user).order_by('-scanned_at')[:5]
    alerts = []
    if events.exists():
        alerts.append(ThreatAlert(title='Suspicious login pattern detected', summary='Our behavioral analysis identified unusual access activity.', severity='High', source='Behavioral AI'))
    if scans.exists() and not scans.first().is_safe:
        alerts.append(ThreatAlert(title='Potential phishing website', summary='A recently scanned domain shows phishing indicators and low reputation.', severity='Critical', source='Threat Intelligence'))
    if not alerts:
        alerts.append(ThreatAlert(title='No active threats detected', summary='Your current environment appears stable. Continue monitoring for changes.', severity='Low', source='AI Review'))

    context = {
        'alerts': alerts,
        'events': events,
        'scans': scans,
    }
    return render(request, 'threats/home.html', context)
