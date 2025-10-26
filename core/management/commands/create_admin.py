from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile


class Command(BaseCommand):
    help = 'Creates a superuser with admin privileges'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='admin', help='Username for the superuser')
        parser.add_argument('--email', type=str, default='admin@infinihumanizer.local', help='Email for the superuser')
        parser.add_argument('--password', type=str, default='admin123', help='Password for the superuser')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'User "{username}" already exists!'))
            user = User.objects.get(username=username)
            if not user.is_superuser:
                user.is_superuser = True
                user.is_staff = True
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Updated "{username}" to superuser status'))
            else:
                self.stdout.write(self.style.SUCCESS(f'User "{username}" is already a superuser'))
        else:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created superuser "{username}"'))
            
        # Ensure profile exists
        profile, created = Profile.objects.get_or_create(user=user)
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created profile for "{username}"'))
        
        self.stdout.write(self.style.SUCCESS('---'))
        self.stdout.write(self.style.SUCCESS(f'Username: {username}'))
        self.stdout.write(self.style.SUCCESS(f'Email: {email}'))
        self.stdout.write(self.style.WARNING(f'Password: {password}'))
        self.stdout.write(self.style.SUCCESS('---'))
        self.stdout.write(self.style.WARNING('⚠️  SECURITY: Clear your console history after viewing the password'))
        self.stdout.write(self.style.SUCCESS('You can now login to /admin/ with these credentials'))
