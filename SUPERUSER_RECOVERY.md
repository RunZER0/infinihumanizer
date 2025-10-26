# Superuser Credential Recovery Guide

## Problem
You've forgotten your superuser (admin) credentials and need to create a new admin account or reset the password.

## Solution

We've created a Django management command that will create a new superuser with auto-generated secure credentials.

### Quick Steps

1. **Open your terminal** in the project directory

2. **Make sure your virtual environment is activated** (if you're using one):
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Mac/Linux
   source venv/bin/activate
   ```

3. **Run the command**:
   ```bash
   python manage.py create_new_superuser
   ```

4. **Save the credentials shown** - they look like this:
   ```
   ======================================================================
   SUPERUSER CREDENTIALS
   ======================================================================
   Username: admin
   Email:    admin@infinihumanizer.local
   Password: aB3$dEf7!hJ9kL2m
   ======================================================================
   
   ⚠️  IMPORTANT: Save these credentials in a secure location!
      This password will not be shown again.
   ```

5. **Log in** using these credentials at:
   - Django Admin: `http://localhost:8000/admin/`
   - Application: `http://localhost:8000/accounts/login/`

### If You Want to Reset an Existing User

If you want to reset the password for the existing "admin" user:

```bash
python manage.py create_new_superuser --update-existing
```

### If You Want Custom Username/Email

```bash
python manage.py create_new_superuser --email your@email.com --username yourusername
```

### For Production/Remote Server

If you're running this on a remote server (like Render, Heroku, etc.):

**For Render:**
```bash
# In your Render dashboard, go to Shell and run:
python manage.py create_new_superuser
```

**For Heroku:**
```bash
heroku run python manage.py create_new_superuser
```

**For other servers:**
```bash
# SSH into your server first, then:
cd /path/to/your/project
python manage.py create_new_superuser
```

## Security Notes

1. **Save the password immediately** - it's only shown once
2. **Use a password manager** to store these credentials securely
3. **Consider changing the password** after first login if you prefer a custom one
4. **Don't share** these credentials or commit them to git

## Troubleshooting

### "No module named django"
- Make sure you've activated your virtual environment
- Install dependencies: `pip install -r requirements.txt`

### "Database connection error"
- Ensure your database is running
- Check that migrations are applied: `python manage.py migrate`
- Verify your `.env` file has correct database settings

### "User already exists"
- Use `--update-existing` flag to reset the password
- Or use `--username differentname` to create a different admin

### "Command not found"
- Make sure you're in the project root directory (where `manage.py` is)
- Verify the command file exists at `core/management/commands/create_new_superuser.py`

## What This Command Does

1. Generates a secure 16-character random password with:
   - Uppercase letters
   - Lowercase letters
   - Numbers
   - Special characters

2. Creates or updates a superuser account with:
   - Full admin privileges
   - Active status
   - The generated password (securely hashed in the database)

3. Displays the credentials for you to save

## Additional Help

For more detailed documentation, see:
- [core/management/commands/README.md](core/management/commands/README.md)
- [README.md](README.md) - Main project documentation

## Contact

If you still have issues, please check the project documentation or reach out to the development team.
