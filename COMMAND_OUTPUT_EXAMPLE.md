# create_new_superuser Command - Output Example

This file shows what you'll see when you run the command successfully.

## Command

```bash
python manage.py create_new_superuser
```

## Output

```
======================================================================
Creating New Superuser
======================================================================


✓ New superuser created successfully!

======================================================================
SUPERUSER CREDENTIALS
======================================================================
Username: admin
Email:    admin@infinihumanizer.local
Password: aB3$dEf7!hJ9kL2m
======================================================================

⚠️  IMPORTANT: Save these credentials in a secure location!
   This password will not be shown again.

You can now log in to the Django admin at /admin/
or the application at /accounts/login/
```

## With Custom Options

### Command with custom email and username

```bash
python manage.py create_new_superuser --email superadmin@company.com --username superadmin
```

### Output

```
======================================================================
Creating New Superuser
======================================================================


✓ New superuser created successfully!

======================================================================
SUPERUSER CREDENTIALS
======================================================================
Username: superadmin
Email:    superadmin@company.com
Password: X9!kL#mN2pQ$rS5t
======================================================================

⚠️  IMPORTANT: Save these credentials in a secure location!
   This password will not be shown again.

You can now log in to the Django admin at /admin/
or the application at /accounts/login/
```

## Updating Existing User

### Command to reset password

```bash
python manage.py create_new_superuser --update-existing
```

### Output

```
======================================================================
Creating New Superuser
======================================================================

User "admin" already exists. Updating password...

✓ Superuser password updated successfully!

======================================================================
SUPERUSER CREDENTIALS
======================================================================
Username: admin
Email:    admin@infinihumanizer.local
Password: V7#wX@yZ1aB$cD3e
======================================================================

⚠️  IMPORTANT: Save these credentials in a secure location!
   This password will not be shown again.

You can now log in to the Django admin at /admin/
or the application at /accounts/login/
```

## Error: User Already Exists

If you try to create a user that already exists without `--update-existing`:

### Command

```bash
python manage.py create_new_superuser --username admin
```

### Output

```
======================================================================
Creating New Superuser
======================================================================


✗ Error: User "admin" already exists.
  Use --update-existing to update the password, or
  Use --username to specify a different username.
```

## What to Do Next

1. **Copy the password** - Store it in a password manager
2. **Log in** - Use the credentials at `/admin/` or `/accounts/login/`
3. **Verify access** - Make sure you can log in successfully
4. **(Optional) Change password** - You can change it later in the admin panel if desired

## Security Reminders

- ✅ The password is only shown once
- ✅ It's stored securely (hashed) in the database
- ✅ It contains uppercase, lowercase, numbers, and special characters
- ✅ It's 16 characters long for maximum security
- ⚠️ Never commit this password to version control
- ⚠️ Don't share it in screenshots or logs
