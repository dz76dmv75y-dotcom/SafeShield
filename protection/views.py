from urllib.parse import urlparse

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from notifications.models import Notification

from .forms import ProtectedAccountForm
from .models import ProtectedAccount, SecurityEvent


def analyze_banking_url(url):
    parsed = urlparse(url)
    host = (parsed.netloc or '').lower()
    path = (parsed.path or '').lower()
    suspicious_terms = ['verify', 'update', 'secure', 'login', 'support', 'claim', 'reset', 'urgent', 'banking']
    suspicious_hits = [term for term in suspicious_terms if term in path]
    risk_level = 'Low'
    is_suspicious = False
    reasons = []

    if not parsed.scheme or not parsed.netloc:
        return {
            'is_suspicious': True,
            'risk_level': 'High',
            'reasons': ['The URL is incomplete or malformed.'],
            'recommendation': 'Do not open the link. Verify the official site directly through your browser or app.',
            'score': 95,
        }

    if parsed.scheme != 'https':
        reasons.append('The link does not use HTTPS, which increases the chance of interception.')
        is_suspicious = True
        risk_level = 'Medium'

    if any(term in host for term in ['paypal', 'secure', 'verify', 'login', 'banking', 'support']) or any(term in path for term in ['verify', 'update', 'login', 'support']):
        reasons.append('The address contains common phishing styling such as login, support, or secure wording.')
        is_suspicious = True
        risk_level = 'High'

    if any(term in host for term in ['example', 'xyz', 'top', 'click', 'link']) or host.count('.') < 2:
        reasons.append('The domain structure appears unusual for a trusted financial service.')
        is_suspicious = True
        risk_level = 'High'

    if not reasons:
        reasons.append('The destination appears consistent with a normal banking URL and uses HTTPS.')

    if suspicious_hits:
        reasons.append(f'Observed risk keywords: {", ".join(suspicious_hits)}')

    score = 20 if risk_level == 'Low' else 70 if risk_level == 'Medium' else 92
    recommendation = 'Treat the URL as suspicious and do not enter credentials. Verify the official website by typing the address manually.' if is_suspicious else 'The URL appears consistent with a legitimate banking destination. Continue with caution and verify the domain.'
    return {
        'is_suspicious': is_suspicious,
        'risk_level': risk_level,
        'reasons': reasons,
        'recommendation': recommendation,
        'score': score,
    }


@login_required
def accounts_view(request):
    accounts = ProtectedAccount.objects.filter(user=request.user).order_by('-created_at')
    if request.method == 'POST':
        form = ProtectedAccountForm(request.POST)
        if form.is_valid():
            ProtectedAccount.objects.create(
                user=request.user,
                account_type=form.cleaned_data['account_type'],
                name=form.cleaned_data['name'],
                username=form.cleaned_data['username'],
                status='Protected',
                security_recommendation='Enable MFA and review recent activity.',
                notes=form.cleaned_data['notes'],
            )
            Notification.objects.create(user=request.user, title='Protected Account Added', body='Your new account is now included in the protection center.', category='protection')
            messages.success(request, 'Account protection entry added.')
            return redirect('protection:accounts')
    else:
        form = ProtectedAccountForm()
    return render(request, 'protection/accounts.html', {'accounts': accounts, 'form': form})


@login_required
def events_view(request):
    events = SecurityEvent.objects.filter(user=request.user).order_by('-created_at')[:15]
    return render(request, 'protection/events.html', {'events': events})


@login_required
def simulate_protection(request):
    if request.method == 'POST':
        target = request.POST.get('url', '').strip()
        if target:
            SecurityEvent.objects.create(
                user=request.user,
                event_type='web_protection',
                title='Suspicious website approached',
                details=f'{target} was flagged for suspicious behavior and is recommended for blocking.',
                severity='high',
                source='Protection Monitor',
            )
            Notification.objects.create(user=request.user, title='Protection Warning', body=f'We recommend blocking {target} due to suspicious patterns.', category='warning')
            messages.warning(request, 'A suspicious website was identified and logged for review.')
            return redirect('protection:events')
    return render(request, 'protection/simulate.html')


@login_required
def banking_security(request):
    recommendations = [
        'Enable multi-factor authentication for your banking and payment accounts.',
        'Verify the website address directly in your browser before entering credentials.',
        'Review recent logins and immediately change your password if anything looks unusual.',
        'Use a dedicated password manager and avoid saving banking credentials in browsers or email.',
    ]
    recent_events = SecurityEvent.objects.filter(user=request.user, event_type__in=['banking_scan', 'banking_takeover']).order_by('-created_at')[:8]

    if request.method == 'POST':
        target = request.POST.get('url', '').strip()
        result = analyze_banking_url(target)
        is_suspicious = result['is_suspicious']
        severity = 'critical' if is_suspicious and result['risk_level'] == 'High' else 'high' if is_suspicious else 'info'
        SecurityEvent.objects.create(
            user=request.user,
            event_type='banking_scan',
            title='Banking URL analysis completed',
            details=f'{target} was evaluated for phishing and scam indicators with a {result["risk_level"]} risk level.',
            severity=severity,
            source='Banking Protection',
        )
        if is_suspicious:
            SecurityEvent.objects.create(
                user=request.user,
                event_type='banking_takeover',
                title='Possible account-takeover warning',
                details='A suspicious banking URL was detected. Avoid entering credentials and verify the website directly.',
                severity='critical',
                source='Banking Protection',
            )
            Notification.objects.create(user=request.user, title='Banking Warning', body='A suspicious banking URL was detected. Avoid entering credentials and verify the destination through your bank’s official app or website.', category='warning')
            messages.warning(request, 'Suspicious banking URL detected. SafeShield recommends blocking it and verifying the destination directly.')
        else:
            Notification.objects.create(user=request.user, title='Banking Check Passed', body='The evaluated URL appears consistent with a trusted financial destination.', category='info')
            messages.success(request, 'The banking URL appears safe. Continue with caution and verify the domain manually.')
        return render(request, 'protection/banking_security.html', {'analysis': result, 'recommendations': recommendations, 'recent_events': recent_events})

    return render(request, 'protection/banking_security.html', {'analysis': None, 'recommendations': recommendations, 'recent_events': recent_events})
