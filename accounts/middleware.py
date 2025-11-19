"""
Device tracking middleware for Kenya plans with device limits.
"""
import hashlib
import logging
from datetime import date
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import redirect
from accounts.models import DeviceSession


logger = logging.getLogger(__name__)


def get_device_fingerprint(request):
    """
    Generate a unique fingerprint for the device based on User-Agent and IP.
    This is a simple implementation - for production you might want to use
    more sophisticated browser fingerprinting.
    """
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    ip_address = get_client_ip(request)
    
    # Create a hash from user agent and IP
    fingerprint_string = f"{user_agent}:{ip_address}"
    fingerprint = hashlib.sha256(fingerprint_string.encode()).hexdigest()
    
    return fingerprint


def get_client_ip(request):
    """Get the client's real IP address."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class DeviceLimitMiddleware:
    """
    Middleware to enforce device limits for Kenya plans:
    - Basic plans (KE_DAILY, KE_WEEKLY, KE_MONTHLY): 1 device at a time, max 3 different devices per day
    - Multi-device plan (KE_MULTI_DEVICE): up to 5 concurrent devices
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Paths that don't require device checking
        self.exempt_paths = [
            '/accounts/login/',
            '/accounts/logout/',
            '/accounts/signup/',
            '/accounts/password/',
            '/static/',
            '/media/',
            '/admin/',
        ]
    
    def __call__(self, request):
        # Check if path is exempt or user is not authenticated
        if not request.user.is_authenticated or any(request.path.startswith(path) for path in self.exempt_paths):
            return self.get_response(request)
        
        # Get user profile
        try:
            profile = request.user.profile
        except:
            # No profile yet, let it pass
            return self.get_response(request)
        
        # Only enforce for Kenya plans
        if not profile.is_kenya_plan():
            return self.get_response(request)
        
        # Check if plan is expired
        if profile.plan_expires_at and timezone.now() > profile.plan_expires_at:
            messages.error(request, "Your plan has expired. Please renew to continue using the humanizer.")
            return redirect('pricing')
        
        # Get device fingerprint
        device_fingerprint = get_device_fingerprint(request)
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Get or create device session
        session, created = DeviceSession.objects.get_or_create(
            user=request.user,
            device_fingerprint=device_fingerprint,
            defaults={
                'ip_address': ip_address,
                'user_agent': user_agent,
                'is_active': True
            }
        )
        
        # Update last_seen for existing session
        if not created:
            session.last_seen = timezone.now()
            session.is_active = True
            session.save(update_fields=['last_seen', 'is_active'])
        
        # Reset daily counter if it's a new day
        today = date.today()
        if profile.last_device_reset != today:
            profile.daily_device_switches = 0
            profile.last_device_reset = today
            profile.save(update_fields=['daily_device_switches', 'last_device_reset'])
        
        # Count active devices (active in last 10 minutes)
        ten_minutes_ago = timezone.now() - timezone.timedelta(minutes=10)
        active_devices = DeviceSession.objects.filter(
            user=request.user,
            is_active=True,
            last_seen__gte=ten_minutes_ago
        ).count()
        
        # Count unique devices used today
        devices_today = DeviceSession.objects.filter(
            user=request.user,
            last_seen__date=today
        ).count()
        
        # Enforce limits based on plan type
        if profile.account_type == 'KE_MULTI_DEVICE':
            # Multi-device plan: up to 5 concurrent devices, max 5 different devices per day
            max_concurrent = 5
            max_daily_devices = 5
            
            if active_devices > max_concurrent:
                messages.error(
                    request,
                    f"Device limit reached. Your Multi-Device plan allows up to {max_concurrent} devices at once. "
                    f"Please log out from another device."
                )
                return redirect('settings')
                
            if devices_today > max_daily_devices:
                messages.error(
                    request,
                    f"Daily device limit reached. To prevent abuse, even Multi-Device plans are limited to {max_daily_devices} unique devices per day."
                )
                return redirect('pricing')
        else:
            # Basic Kenya plans: 1 device at a time, max 3 different devices per day
            max_concurrent = 1
            max_daily_devices = 3
            
            if active_devices > max_concurrent:
                # Deactivate all other devices
                DeviceSession.objects.filter(
                    user=request.user,
                    is_active=True
                ).exclude(device_fingerprint=device_fingerprint).update(is_active=False)
                
                messages.warning(
                    request,
                    "Your previous device session has been logged out. Only 1 device can be active at a time on your plan."
                )
            
            if devices_today > max_daily_devices:
                messages.error(
                    request,
                    f"Daily device limit reached. You can use up to {max_daily_devices} different devices per day. "
                    f"Upgrade to Multi-Device plan for unlimited device switching."
                )
                return redirect('pricing')
        
        # Update profile with current counts
        profile.current_active_devices = active_devices
        profile.save(update_fields=['current_active_devices'])
        
        return self.get_response(request)
