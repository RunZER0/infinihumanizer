"""
Management command to activate users who have completed WhatsApp verification.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from allauth.account.models import EmailAddress
from accounts.models import WhatsAppVerification


class Command(BaseCommand):
    help = 'Activate users who have verified WhatsApp but are still inactive'

    def handle(self, *args, **options):
        users = User.objects.filter(is_active=False)
        activated_count = 0
        
        self.stdout.write(f"📊 Found {users.count()} inactive users")
        
        for user in users:
            # Check if they have verified WhatsApp
            whatsapp_verified = WhatsAppVerification.objects.filter(
                user=user, 
                is_verified=True
            ).exists()
            
            if whatsapp_verified:
                # Activate the user
                user.is_active = True
                user.save()
                
                # Ensure EmailAddress is verified
                EmailAddress.objects.update_or_create(
                    user=user,
                    email=user.email,
                    defaults={'verified': True, 'primary': True}
                )
                
                activated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Activated {user.email}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  {user.email} - WhatsApp not verified yet')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Done! Activated {activated_count} users.'
            )
        )
