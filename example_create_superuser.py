#!/usr/bin/env python
"""
Example script showing how to programmatically use the create_new_superuser command.
This is useful for automated deployment scripts or testing.

Note: In most cases, you should use the command directly:
    python manage.py create_new_superuser
"""

import os
import sys
import django

# Add the project directory to the path
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_dir)

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.core.management import call_command
from io import StringIO

def example_create_default_superuser():
    """Example: Create a superuser with default settings"""
    print("Example 1: Creating superuser with default settings")
    print("-" * 60)
    
    # Capture output
    out = StringIO()
    
    try:
        # Call the command
        call_command('create_new_superuser', stdout=out, skip_checks=True)
        
        # Print the output
        print(out.getvalue())
    except Exception as e:
        print(f"Error: {e}")

def example_create_custom_superuser():
    """Example: Create a superuser with custom username and email"""
    print("\nExample 2: Creating superuser with custom settings")
    print("-" * 60)
    
    out = StringIO()
    
    try:
        call_command(
            'create_new_superuser',
            username='customadmin',
            email='custom@example.com',
            stdout=out,
            skip_checks=True
        )
        
        print(out.getvalue())
    except Exception as e:
        print(f"Error: {e}")

def example_update_existing_user():
    """Example: Update existing user's password"""
    print("\nExample 3: Updating existing superuser password")
    print("-" * 60)
    
    out = StringIO()
    
    try:
        call_command(
            'create_new_superuser',
            username='admin',  # Existing username
            update_existing=True,
            stdout=out,
            skip_checks=True
        )
        
        print(out.getvalue())
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    print("=" * 60)
    print("create_new_superuser Command Examples")
    print("=" * 60)
    print("\nThese examples show how to use the command programmatically.")
    print("For normal use, just run:")
    print("    python manage.py create_new_superuser")
    print()
    
    # Run examples
    example_create_default_superuser()
    
    # Uncomment to try other examples:
    # example_create_custom_superuser()
    # example_update_existing_user()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)
