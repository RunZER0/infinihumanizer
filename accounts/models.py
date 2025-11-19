from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

ACCOUNT_CHOICES = [
    ('FREE', 'Free'),
    ('STANDARD', 'Standard'),
    ('PRO', 'Pro'),
    ('ENTERPRISE', 'Enterprise'),
    # Kenya-specific plans
    ('KE_DAILY', 'Kenya Daily'),
    ('KE_WEEKLY', 'Kenya Weekly'),
    ('KE_MONTHLY', 'Kenya Monthly'),
    ('KE_MULTI_DEVICE', 'Kenya Multi-Device'),
]

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    word_quota = models.IntegerField(default=1000)
    words_used = models.IntegerField(default=0)
    is_paid = models.BooleanField(default=False)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_CHOICES, default='FREE')
    
    # Currency and location
    currency = models.CharField(max_length=3, default='USD', choices=[('USD', 'US Dollar'), ('KES', 'Kenyan Shilling')])
    
    # Device tracking for Kenya plans
    max_concurrent_devices = models.IntegerField(default=1, help_text="Maximum devices that can be logged in simultaneously")
    current_active_devices = models.IntegerField(default=0, help_text="Currently active device sessions")
    daily_device_switches = models.IntegerField(default=0, help_text="Number of different devices used today")
    last_device_reset = models.DateField(null=True, blank=True, help_text="Last date device counter was reset")
    
    # Plan expiry for time-based plans
    plan_expires_at = models.DateTimeField(null=True, blank=True, help_text="When the current plan expires")

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def has_quota(self, new_words):
        # Kenya unlimited plans (time-based, not word-based)
        if self.account_type in ['KE_DAILY', 'KE_WEEKLY', 'KE_MONTHLY', 'KE_MULTI_DEVICE']:
            # Check if plan is still active
            if self.plan_expires_at:
                from django.utils import timezone
                return timezone.now() < self.plan_expires_at
            return False
            
        # Word-based plans (original behavior)
        if self.is_paid:
            return True
        return (self.words_used + new_words) <= self.word_quota
    
    def is_kenya_plan(self):
        """Check if user is on a Kenya-specific plan"""
        return self.account_type.startswith('KE_')

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()

# accounts/models.py

from django.db import models
from django.contrib.auth.models import User

class EmailVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_verified = models.BooleanField(default=False)
    token = models.CharField(max_length=64, blank=True, null=True)  # for your email links
    created_at = models.DateTimeField(auto_now_add=True)


class WhatsAppVerification(models.Model):
    """
    Stores verification codes for WhatsApp-based signup approval.
    Uses morse code encoding (A-J representing digits 1-0).
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='whatsapp_verification')
    encoded_code = models.CharField(max_length=6, help_text="Morse code (A-J)")
    numeric_code = models.CharField(max_length=6, help_text="Actual 6-digit code")
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"WhatsApp verification for {self.user.email} - {'Verified' if self.is_verified else 'Pending'}"


class DeviceSession(models.Model):
    """
    Tracks active device sessions for users on Kenya plans with device limits.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='device_sessions')
    device_fingerprint = models.CharField(max_length=255, help_text="Unique device identifier hash")
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'device_fingerprint']
        ordering = ['-last_seen']
    
    def __str__(self):
        return f"{self.user.username} - {self.device_fingerprint[:16]}... ({'Active' if self.is_active else 'Inactive'})"


