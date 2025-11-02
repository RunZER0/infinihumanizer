"""
Management command to create missing EmailAddress records for existing users.
Run this after database migration to fix authentication issues.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from allauth.account.models import EmailAddress


class Command(BaseCommand):
    help = 'Create EmailAddress records for users who are missing them'

    def handle(self, *args, **options):
        users = User.objects.all()
        total_users = users.count()
        created_count = 0
        updated_count = 0
        
        self.stdout.write(f"📊 Found {total_users} users in database")
        
        if total_users == 0:
            self.stdout.write(
                self.style.WARNING('⚠️  No users found in database! Database might be empty.')
            )
            return
        
        for user in users:
            self.stdout.write(f"   Checking user: {user.email} (is_active={user.is_active})")
            
            email_address, created = EmailAddress.objects.get_or_create(
                user=user,
                email=user.email,
                defaults={
                    'verified': user.is_active,  # If user is active, they're verified
                    'primary': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Created EmailAddress for {user.email}')
                )
            else:
                # Update existing record to match user's active status
                if email_address.verified != user.is_active:
                    email_address.verified = user.is_active
                    email_address.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Updated EmailAddress for {user.email}')
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Done! Created {created_count} and updated {updated_count} EmailAddress records.'
            )
        )
