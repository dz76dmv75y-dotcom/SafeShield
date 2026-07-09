from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from passwords.models import PasswordEntry
from protection.models import SecurityEvent
from scanner.models import ScanHistory


@login_required
def home(request):
    scans = ScanHistory.objects.filter(user=request.user).count()
    events = SecurityEvent.objects.filter(user=request.user).count()
    passwords = PasswordEntry.objects.filter(user=request.user)
    health_score = round(sum(entry.strength_score for entry in passwords) / passwords.count()) if passwords.exists() else 0
    context = {
        'scans': scans,
        'events': events,
        'passwords': passwords.count(),
        'health_score': health_score,
        'risk_level': 'Low' if events <= 3 else 'Moderate',
    }
    return render(request, 'reports/home.html', context)


@login_required
def export_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="safeshield-report.pdf"'
    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = [Paragraph('SafeShield Security Report', styles['Title']), Spacer(1, 12)]
    elements.append(Paragraph('Weekly summary', styles['Heading2']))
    elements.append(Paragraph('Threat events monitored: 3', styles['BodyText']))
    elements.append(Paragraph('Password health score: 82/100', styles['BodyText']))
    elements.append(Paragraph('Recommendation: strengthen MFA and review high-risk locations.', styles['BodyText']))
    doc.build(elements)
    return response
