# Superuser Management

This directory contains Django management commands for user administration.

## Create New Superuser

If you've forgotten your superuser credentials or need to create a new administrator account, use the `create_new_superuser` management command.

### Basic Usage

```bash
python manage.py create_new_superuser
```

This will create a new superuser with:
- **Username:** admin
- **Email:** admin@infinihumanizer.local
- **Password:** (automatically generated and displayed)

### Custom Email and Username

```bash
python manage.py create_new_superuser --email your@email.com --username yourusername
```

### Update Existing User

If the user already exists and you want to reset their password:

```bash
python manage.py create_new_superuser --update-existing
```

Or with custom username:

```bash
python manage.py create_new_superuser --username existing_user --update-existing
```

### Important Notes

1. **Save the credentials immediately** - The generated password is displayed only once for security reasons.
2. **Production use** - Always use this command in a secure environment. Never share the output in logs or screenshots.
3. **Email verification** - In production with email verification enabled, you may need to verify the email or disable verification temporarily.

### Examples

#### Scenario 1: Forgotten credentials (default admin user)
```bash
python manage.py create_new_superuser --update-existing
```

#### Scenario 2: Create a new admin with specific email
```bash
python manage.py create_new_superuser --email superadmin@company.com --username superadmin
```

#### Scenario 3: Development/Testing
```bash
python manage.py create_new_superuser --email dev@test.local --username testadmin
```

### Security Best Practices

1. **Change the password** after first login if desired
2. **Use a password manager** to store the generated credentials
3. **Limit superuser accounts** - Only create what you need
4. **Regular audits** - Review superuser accounts periodically

### Troubleshooting

#### Database not ready
If you get a database connection error, ensure:
- The database is running
- Migrations have been applied: `python manage.py migrate`
- Environment variables are configured correctly

#### User already exists
- Use `--update-existing` flag to reset the password
- Or use `--username` to create a different user

#### Permission denied
- Ensure you have proper permissions to write to the database
- Check that the Django application can connect to the database

### After Creating Superuser

You can log in at:
- Django Admin: `http://your-domain/admin/`
- Application Login: `http://your-domain/accounts/login/`

For local development:
- Django Admin: `http://localhost:8000/admin/`
- Application Login: `http://localhost:8000/accounts/login/`
