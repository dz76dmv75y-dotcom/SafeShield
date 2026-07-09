import base64
import hashlib

from cryptography.fernet import Fernet
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render


def _get_cipher():
    digest = hashlib.sha256(settings.SECRET_KEY.encode('utf-8')).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


@login_required
def home(request):
    return render(request, 'encryption/home.html')


@login_required
def encrypt_text(request):
    if request.method == 'POST':
        payload = request.POST.get('payload', '')
        encrypted = _get_cipher().encrypt(payload.encode('utf-8')).decode('utf-8')
        messages.success(request, 'Text encrypted successfully.')
        return render(request, 'encryption/home.html', {'encrypted_text': encrypted})
    return redirect('encryption:home')


@login_required
def decrypt_text(request):
    if request.method == 'POST':
        payload = request.POST.get('payload', '')
        decrypted = _get_cipher().decrypt(payload.encode('utf-8')).decode('utf-8')
        messages.success(request, 'Text decrypted successfully.')
        return render(request, 'encryption/home.html', {'decrypted_text': decrypted})
    return redirect('encryption:home')


@login_required
def encrypt_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded = request.FILES['file']
        data = uploaded.read()
        encrypted = _get_cipher().encrypt(data)
        response = HttpResponse(encrypted, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="encrypted_{uploaded.name}"'
        return response
    messages.error(request, 'Please upload a file to encrypt.')
    return redirect('encryption:home')


@login_required
def decrypt_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded = request.FILES['file']
        data = uploaded.read()
        decrypted = _get_cipher().decrypt(data)
        response = HttpResponse(decrypted, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="decrypted_{uploaded.name}"'
        return response
    messages.error(request, 'Please upload an encrypted file to decrypt.')
    return redirect('encryption:home')
