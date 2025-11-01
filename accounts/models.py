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
]

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    word_quota = models.IntegerField(default=1000)
    words_used = models.IntegerField(default=0)
    is_paid = models.BooleanField(default=False)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_CHOICES, default='FREE')

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def has_quota(self, new_words):
        if self.is_paid:
            return True
        return (self.words_used + new_words) <= self.word_quota

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


