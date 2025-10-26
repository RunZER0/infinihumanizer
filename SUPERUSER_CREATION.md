# Superuser Creation Guide

## Creating a Superuser

To create a superuser for accessing the Django admin panel, use the `create_admin` management command:

### Default Usage

```bash
python manage.py create_admin
```

This will create a superuser with:
- **Username:** admin
- **Email:** admin@infinihumanizer.local
- **Password:** admin123

### Custom Credentials

You can specify custom credentials using command-line arguments:

```bash
python manage.py create_admin --username myusername --email admin@example.com --password MySecurePass123!
```

### Arguments

- `--username`: Username for the superuser (default: `admin`)
- `--email`: Email for the superuser (default: `admin@infinihumanizer.local`)
- `--password`: Password for the superuser (default: `admin123`)

### Accessing the Admin Panel

After creating the superuser, you can access the admin panel at:

```
http://localhost:8000/admin/
```

Or for production:

```
https://yourdomain.com/admin/
```

### Notes

- If a user with the specified username already exists, the command will update them to have superuser privileges
- A profile will be automatically created for the superuser if it doesn't exist
- The command outputs the credentials for easy reference

### Example Output

```
Successfully created superuser "admin"
Created profile for "admin"
---
Username: admin
Email: admin@infinihumanizer.local
Password: admin123
---
You can now login to /admin/ with these credentials
```
