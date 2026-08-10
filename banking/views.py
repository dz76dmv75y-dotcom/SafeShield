from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from notifications.models import Notification
from protection.models import ProtectedAccount, SecurityEvent

from .forms import BankingAccountForm


@login_required
def home(request):
    form = BankingAccountForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        ProtectedAccount.objects.create(
            user=request.user,
            account_type='banking',
            name=form.cleaned_data['institution'],
            username=form.cleaned_data['account_number'] or '',
            status='Protected',
            security_recommendation='Keep your banking credentials safe and enable MFA.',
            notes=form.cleaned_data['notes'],
        )
        Notification.objects.create(
            user=request.user,
            title='Bank account added',
            body='Your banking account was added to SafeShield monitoring.',
            category='banking',
        )
        messages.success(request, 'Your bank account has been added to the protection center.')
        return redirect('banking:home')

    banking_accounts = ProtectedAccount.objects.filter(
        user=request.user,
        account_type='banking'
    ).order_by('-created_at')

    recent_alerts = SecurityEvent.objects.filter(
        user=request.user,
        event_type__in=['banking_scan', 'banking_takeover']
    ).order_by('-created_at')[:5]

    return render(
        request,
        'banking/home.html',
        {
            'form': form,
            'banking_accounts': banking_accounts,
            'recent_alerts': recent_alerts,
            'banking_count': banking_accounts.count(),
            'checks_count': recent_alerts.count(),
        },
    )
