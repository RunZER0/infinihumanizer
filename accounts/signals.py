from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver
from .models import DeviceSession
import hashlib

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@receiver(user_logged_out)
def deactivate_device_session(sender, user, request, **kwargs):
    if user and request:
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        ip_address = get_client_ip(request)
        fingerprint_string = f"{user_agent}:{ip_address}"
        device_fingerprint = hashlib.sha256(fingerprint_string.encode()).hexdigest()
        
        # Deactivate the specific session
        DeviceSession.objects.filter(
            user=user,
            device_fingerprint=device_fingerprint
        ).update(is_active=False)
