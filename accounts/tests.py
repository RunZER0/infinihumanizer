from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import Profile


class SignupViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('account_signup')
    
    def test_signup_view_get(self):
        """Test that signup page loads successfully"""
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/signup.html')
    
    def test_signup_creates_user_and_profile(self):
        """Test that signup creates both user and profile"""
        signup_data = {
            'email': 'testuser@example.com',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
        }
        
        response = self.client.post(self.signup_url, signup_data)
        
        # Should redirect to humanizer after successful signup
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('humanizer'), fetch_redirect_response=False)
        
        # User should be created with auto-generated username
        user = User.objects.get(email='testuser@example.com')
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'testuser')  # Generated from email
        
        # Profile should be created
        profile = Profile.objects.get(user=user)
        self.assertIsNotNone(profile)
        self.assertEqual(profile.word_quota, 1000)  # Default quota
        
        # User should be logged in after signup
        self.assertTrue(response.wsgi_request.user.is_authenticated)
    
    def test_signup_with_duplicate_email_username(self):
        """Test that duplicate username is handled by appending number"""
        # Create first user
        User.objects.create_user(username='testuser', email='first@example.com', password='pass123')
        
        # Try to create second user with email that would generate same username
        signup_data = {
            'email': 'testuser@different.com',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
        }
        
        response = self.client.post(self.signup_url, signup_data)
        
        # Should succeed with modified username
        self.assertEqual(response.status_code, 302)
        
        # Second user should exist with username 'testuser1'
        user = User.objects.get(email='testuser@different.com')
        self.assertEqual(user.username, 'testuser1')
