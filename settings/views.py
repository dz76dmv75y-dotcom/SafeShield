from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import PreferenceForm
from .models import UserPreference


@login_required
def preferences_view(request):
    preference, _ = UserPreference.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = PreferenceForm(request.POST, instance=preference)
        if form.is_valid():
            form.save()
            messages.success(request, 'Preferences updated successfully.')
            return redirect('settings:preferences')
    else:
        form = PreferenceForm(instance=preference)
    return render(request, 'settings/preferences.html', {'form': form})
