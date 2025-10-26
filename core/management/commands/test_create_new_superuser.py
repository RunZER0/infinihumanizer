"""
Unit tests for the create_new_superuser management command.
"""
import string
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import CommandError
from io import StringIO
from core.management.commands.create_new_superuser import generate_secure_password


class GeneratePasswordTest(TestCase):
    """Test password generation function"""
    
    def test_password_length(self):
        """Test that password has correct length"""
        password = generate_secure_password(16)
        self.assertEqual(len(password), 16)
        
        password = generate_secure_password(20)
        self.assertEqual(len(password), 20)
    
    def test_password_has_variety(self):
        """Test that password contains different character types"""
        password = generate_secure_password(16)
        
        has_lower = any(c in string.ascii_lowercase for c in password)
        has_upper = any(c in string.ascii_uppercase for c in password)
        has_digit = any(c in string.digits for c in password)
        has_special = any(c in string.punctuation for c in password)
        
        self.assertTrue(has_lower, "Password should contain lowercase letters")
        self.assertTrue(has_upper, "Password should contain uppercase letters")
        self.assertTrue(has_digit, "Password should contain digits")
        self.assertTrue(has_special, "Password should contain special characters")
    
    def test_password_uniqueness(self):
        """Test that generated passwords are unique"""
        passwords = [generate_secure_password(16) for _ in range(10)]
        # All passwords should be unique
        self.assertEqual(len(passwords), len(set(passwords)))


class CreateNewSuperuserCommandTest(TestCase):
    """Test create_new_superuser management command"""
    
    def setUp(self):
        """Clean up any existing test users"""
        User.objects.filter(username='testadmin').delete()
        User.objects.filter(username='admin').delete()
    
    def tearDown(self):
        """Clean up test users"""
        User.objects.filter(username='testadmin').delete()
        User.objects.filter(username='admin').delete()
    
    def test_create_new_superuser_default(self):
        """Test creating a new superuser with default values"""
        out = StringIO()
        call_command('create_new_superuser', stdout=out, skip_checks=True)
        
        output = out.getvalue()
        
        # Check that user was created
        user = User.objects.get(username='admin')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)
        self.assertEqual(user.email, 'admin@infinihumanizer.local')
        
        # Check output contains success message
        self.assertIn('created successfully', output)
        self.assertIn('Username:', output)
        self.assertIn('Password:', output)
    
    def test_create_superuser_custom_values(self):
        """Test creating a superuser with custom username and email"""
        out = StringIO()
        call_command(
            'create_new_superuser',
            username='testadmin',
            email='test@example.com',
            stdout=out,
            skip_checks=True
        )
        
        # Check that user was created with correct values
        user = User.objects.get(username='testadmin')
        self.assertTrue(user.is_superuser)
        self.assertEqual(user.email, 'test@example.com')
    
    def test_duplicate_user_without_update_flag(self):
        """Test that creating duplicate user without update flag fails"""
        # Create initial user
        call_command('create_new_superuser', username='testadmin', skip_checks=True)
        
        # Try to create again without update flag
        out = StringIO()
        call_command('create_new_superuser', username='testadmin', stdout=out, skip_checks=True)
        
        output = out.getvalue()
        self.assertIn('already exists', output)
    
    def test_update_existing_user(self):
        """Test updating an existing user's password"""
        # Create initial user
        call_command('create_new_superuser', username='testadmin', skip_checks=True)
        initial_user = User.objects.get(username='testadmin')
        initial_password_hash = initial_user.password
        
        # Update the user
        out = StringIO()
        call_command(
            'create_new_superuser',
            username='testadmin',
            update_existing=True,
            stdout=out,
            skip_checks=True
        )
        
        # Check password was changed
        updated_user = User.objects.get(username='testadmin')
        self.assertNotEqual(initial_password_hash, updated_user.password)
        
        output = out.getvalue()
        self.assertIn('updated successfully', output)
    
    def test_password_is_usable(self):
        """Test that the generated password can be used to authenticate"""
        out = StringIO()
        call_command('create_new_superuser', username='testadmin', stdout=out, skip_checks=True)
        
        # Extract password from output
        output = out.getvalue()
        # Find password line and extract it
        for line in output.split('\n'):
            if line.strip().startswith('Password:'):
                # Password is printed with ANSI color codes, extract the actual password
                # The format is like "Password: <color_codes>actual_password<color_codes>"
                password_part = line.split('Password:')[1].strip()
                # Remove ANSI color codes if present
                import re
                password = re.sub(r'\x1b\[[0-9;]*m', '', password_part)
                
                # Try to authenticate with the password
                user = User.objects.get(username='testadmin')
                self.assertTrue(user.check_password(password))
                break
