from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from notifications.models import Notification
from protection.models import SecurityEvent

from .models import ScanHistory


def analyze_url(url):
    lowered = url.lower()
    suspicious_terms = ['login', 'paypal', 'appleid', 'bank', 'secure', 'free', 'claim', 'update', 'verify']
    suspicious_hits = [term for term in suspicious_terms if term in lowered]
    is_safe = not suspicious_hits and 'https://' in lowered
    risk_level = 'Critical' if suspicious_hits else 'Low'
    if 'http://' in lowered:
        risk_level = 'Medium'
    reputation = 'Trusted' if is_safe else 'Low Reputation'
    ssl_status = 'Valid SSL' if 'https://' in lowered else 'No SSL / Weak TLS'
    reasons = ['No suspicious keywords detected.'] if is_safe else [f'Observed suspicious patterns: {", ".join(suspicious_hits)}']
    if 'http://' in lowered:
        reasons.append('HTTP is exposed and should be avoided for sensitive pages.')
    summary = 'The website appears safe for general browsing.' if is_safe else 'The website shows multiple indicators of phishing or abuse. Avoid interacting with it.'
    return {
        'is_safe': is_safe,
        'risk_level': risk_level,
        'reputation': reputation,
        'ssl_status': ssl_status,
        'reasons': reasons,
        'summary': summary,
    }


@login_required
def scan_view(request):
    history = ScanHistory.objects.filter(user=request.user).order_by('-scanned_at')[:8]
    if request.method == 'POST':
        target = request.POST.get('url', '').strip()
        if not target:
            messages.error(request, 'Please enter a URL to scan.')
            return redirect('scanner:scan')
        result = analyze_url(target)
        record = ScanHistory.objects.create(
            user=request.user,
            url=target,
            risk_level=result['risk_level'],
            is_safe=result['is_safe'],
            reputation=result['reputation'],
            ssl_status=result['ssl_status'],
            reasons=' | '.join(result['reasons']),
            scan_summary=result['summary'],
        )
        SecurityEvent.objects.create(
            user=request.user,
            event_type='website_scan',
            title='Website scan completed',
            details=f'{target} was evaluated with a {result["risk_level"]} risk rating.',
            severity='high' if not result['is_safe'] else 'info',
            source='Scanner',
        )
        Notification.objects.create(
            user=request.user,
            title='Scan complete',
            body=f'SafeShield evaluated {target} and flagged it as {result["risk_level"]}.',
            category='scan',
        )
        messages.success(request, 'Scan completed successfully.')
        return redirect('scanner:detail', pk=record.pk)
    return render(request, 'scanner/scan.html', {'history': history})


@login_required
def scan_detail(request, pk):
    scan = get_object_or_404(ScanHistory, pk=pk, user=request.user)
    return render(request, 'scanner/detail.html', {'scan': scan})
