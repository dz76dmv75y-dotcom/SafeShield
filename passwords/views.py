from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PasswordEntryForm
from .models import PasswordEntry


def analyze_strength(password):
    score = 0
    if len(password) >= 12:
        score += 40
    if any(ch.isupper() for ch in password):
        score += 15
    if any(ch.isdigit() for ch in password):
        score += 15
    if any(ch in '!@#$%^&*' for ch in password):
        score += 15
    if any(ch.islower() for ch in password):
        score += 15
    return min(100, score)


@login_required
def list_entries(request):
    entries = PasswordEntry.objects.filter(user=request.user).order_by('-created_at')
    health_score = 0
    if entries.exists():
        health_score = round(sum(entry.strength_score for entry in entries) / entries.count())
    return render(request, 'passwords/list.html', {'entries': entries, 'health_score': health_score})


@login_required
def add_entry(request):
    if request.method == 'POST':
        form = PasswordEntryForm(request.POST)
        if form.is_valid():
            raw_password = form.cleaned_data['password']
            PasswordEntry.objects.create(
                user=request.user,
                site=form.cleaned_data['site'],
                username=form.cleaned_data['username'],
                encrypted_value=PasswordEntry.encrypt_password(raw_password),
                notes=form.cleaned_data['notes'],
                strength_score=analyze_strength(raw_password),
                expires_on=form.cleaned_data['expires_on'],
            )
            messages.success(request, 'Password stored securely in your vault.')
            return redirect('passwords:list')
    else:
        form = PasswordEntryForm()
    return render(request, 'passwords/form.html', {'form': form, 'title': 'Store Password'})


@login_required
def edit_entry(request, pk):
    entry = get_object_or_404(PasswordEntry, pk=pk, user=request.user)
    if request.method == 'POST':
        form = PasswordEntryForm(request.POST)
        if form.is_valid():
            entry.site = form.cleaned_data['site']
            entry.username = form.cleaned_data['username']
            entry.encrypted_value = PasswordEntry.encrypt_password(form.cleaned_data['password'])
            entry.notes = form.cleaned_data['notes']
            entry.strength_score = analyze_strength(form.cleaned_data['password'])
            entry.expires_on = form.cleaned_data['expires_on']
            entry.save()
            messages.success(request, 'Password updated.')
            return redirect('passwords:list')
    else:
        form = PasswordEntryForm(initial={'site': entry.site, 'username': entry.username, 'password': entry.password, 'notes': entry.notes, 'expires_on': entry.expires_on})
    return render(request, 'passwords/form.html', {'form': form, 'title': 'Update Password', 'entry': entry})


@login_required
def delete_entry(request, pk):
    entry = get_object_or_404(PasswordEntry, pk=pk, user=request.user)
    entry.delete()
    messages.info(request, 'Password removed from your vault.')
    return redirect('passwords:list')
