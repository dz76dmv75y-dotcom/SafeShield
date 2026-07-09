from ipaddress import ip_address


def get_client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def is_private_ip(value):
    if not value:
        return False
    try:
        return ip_address(value).is_private
    except ValueError:
        return False
