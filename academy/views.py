from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def home(request):
    lessons = [
        {'title': 'Phishing Attacks', 'summary': 'Learn how deceptive messages target users and how to spot them early.'},
        {'title': 'Malware', 'summary': 'Understand common malware behavior and how to reduce exposure.'},
        {'title': 'Ransomware', 'summary': 'Discover how ransomware spreads and how to respond effectively.'},
        {'title': 'Password Security', 'summary': 'Build stronger password habits and avoid common mistakes.'},
        {'title': 'Two-Factor Authentication', 'summary': 'Learn why MFA matters and how to enable it for key accounts.'},
        {'title': 'Social Engineering', 'summary': 'Recognize manipulation tactics that exploit trust and urgency.'},
        {'title': 'Safe Internet Browsing', 'summary': 'Reduce risk by evaluating websites, links, and downloads carefully.'},
        {'title': 'Cybersecurity Tips', 'summary': 'Follow practical habits that reduce exposure across devices and services.'},
    ]
    return render(request, 'academy/home.html', {'lessons': lessons})
