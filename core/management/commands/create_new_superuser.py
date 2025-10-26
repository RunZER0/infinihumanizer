"""
Django management command to create a new superuser with generated credentials.
Useful when superuser credentials are forgotten or need to be reset.
"""
import secrets
import string
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db import transaction
from django.db.utils import IntegrityError


def generate_secure_password(length=16):
    """
    Generate a secure random password with mixed character types.
    
    Args:
        length: Length of the password (default: 16)
    
    Returns:
        A secure random password string
    """
    # Use all character types for a strong password
    characters = string.ascii_letters + string.digits + string.punctuation
    # Ensure at least one of each type is included
    password = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.digits),
        secrets.choice(string.punctuation),
    ]
    # Fill the rest with random characters
    password.extend(secrets.choice(characters) for _ in range(length - 4))
    # Shuffle to avoid predictable patterns
    password_list = list(password)
    secrets.SystemRandom().shuffle(password_list)
    return ''.join(password_list)


class Command(BaseCommand):
    """Django command to create a new superuser with auto-generated credentials"""
    
    help = 'Create a new superuser with auto-generated credentials (useful when credentials are forgotten)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email address for the superuser (default: admin@infinihumanizer.local)',
            default='admin@infinihumanizer.local',
        )
        parser.add_argument(
            '--username',
            type=str,
            help='Username for the superuser (default: admin)',
            default='admin',
        )
        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='Update password if user already exists',
        )

    def handle(self, *args, **options):
        email = options['email']
        username = options['username']
        update_existing = options['update_existing']
        
        self.stdout.write(self.style.WARNING('\n' + '='*70))
        self.stdout.write(self.style.WARNING('Creating New Superuser'))
        self.stdout.write(self.style.WARNING('='*70 + '\n'))
        
        # Generate a secure password
        password = generate_secure_password(16)
        
        try:
            with transaction.atomic():
                # Check if user already exists
                try:
                    user = User.objects.get(username=username)
                    
                    if update_existing:
                        self.stdout.write(
                            self.style.WARNING(
                                f'User "{username}" already exists. Updating password...'
                            )
                        )
                        user.set_password(password)
                        user.email = email
                        user.is_superuser = True
                        user.is_staff = True
                        user.is_active = True
                        user.save()
                        
                        self.stdout.write(self.style.SUCCESS('\n✓ Superuser password updated successfully!\n'))
                    else:
                        self.stdout.write(
                            self.style.ERROR(
                                f'\n✗ Error: User "{username}" already exists.\n'
                                f'  Use --update-existing to update the password, or\n'
                                f'  Use --username to specify a different username.\n'
                            )
                        )
                        return
                        
                except User.DoesNotExist:
                    # Create new superuser
                    user = User.objects.create_superuser(
                        username=username,
                        email=email,
                        password=password
                    )
                    self.stdout.write(self.style.SUCCESS('\n✓ New superuser created successfully!\n'))
                
                # Display credentials
                self.stdout.write(self.style.WARNING('='*70))
                self.stdout.write(self.style.SUCCESS('SUPERUSER CREDENTIALS'))
                self.stdout.write(self.style.WARNING('='*70))
                self.stdout.write(f'Username: {self.style.SUCCESS(username)}')
                self.stdout.write(f'Email:    {self.style.SUCCESS(email)}')
                self.stdout.write(f'Password: {self.style.SUCCESS(password)}')
                self.stdout.write(self.style.WARNING('='*70))
                
                self.stdout.write(
                    self.style.WARNING(
                        '\n⚠️  IMPORTANT: Save these credentials in a secure location!\n'
                        '   This password will not be shown again.\n'
                    )
                )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        '\nYou can now log in to the Django admin at /admin/\n'
                        'or the application at /accounts/login/\n'
                    )
                )
                
        except IntegrityError as e:
            raise CommandError(f'Database error: {str(e)}')
        except Exception as e:
            raise CommandError(f'Error creating superuser: {str(e)}')
