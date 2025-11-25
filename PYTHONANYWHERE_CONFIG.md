# PythonAnywhere Configuration - Smart Aquarium

## Your Account Details

```
Username: TemperatureManag
Database Host: TemperatureManagement.mysql.pythonanywhere-services.com
Database Name: TemperatureManag$smartaquarium_db
```

## Django Settings (settings.py)

Your database is configured as:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'TemperatureManag$smartaquarium_db',
        'USER': 'TemperatureManag',
        'PASSWORD': '[YOUR_PASSWORD_HERE]',  # Add your PythonAnywhere password
        'HOST': 'TemperatureManagement.mysql.pythonanywhere-services.com',
        'PORT': '3306',
    }
}
```

## Next: Add Your Password

You need to update the PASSWORD field with your PythonAnywhere account password.

### How to Update:

1. **On PythonAnywhere Web Console:**
   ```bash
   nano ~/smartaquarium/smartAquarium/settings.py
   ```

2. **Find this line:**
   ```python
   'PASSWORD': 'your_password_here',
   ```

3. **Replace with your PythonAnywhere password:**
   ```python
   'PASSWORD': 'your_actual_pythonanywhere_password',
   ```

4. **Save:** Press `Ctrl+X`, then `Y`, then `Enter`

## Production Settings

Also update in `settings.py`:

```python
DEBUG = False
ALLOWED_HOSTS = ['TemperatureManag.pythonanywhere.com']
STATIC_ROOT = '/home/TemperatureManag/smartaquarium/static'
```

## Setup Steps

1. **Clone repository:**
   ```bash
   cd ~
   git clone https://github.com/dilmithashen6-png/smartaquarium.git
   cd smartaquarium
   ```

2. **Install dependencies:**
   ```bash
   pip install --user -r requirements.txt
   ```

3. **Update password in settings.py** (see above)

4. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Create admin user:**
   ```bash
   python manage.py createsuperuser
   ```

6. **Collect static files:**
   ```bash
   python manage.py collectstatic --noinput
   ```

7. **Configure web app in PythonAnywhere:**
   - Go to Web tab
   - Add new web app (Manual configuration, Python 3.8)
   - WSGI file path: `/home/TemperatureManag/smartaquarium/smartAquarium/wsgi.py`

8. **Reload web app**

## Your Web App URL

Once set up, visit:
```
https://TemperatureManag.pythonanywhere.com
```

## Database Commands

### Connect to MySQL on PythonAnywhere

```bash
mysql -u TemperatureManag -h TemperatureManagement.mysql.pythonanywhere-services.com
# Password: [your PythonAnywhere password]
```

### Show databases

```sql
SHOW DATABASES;
```

### Use your database

```sql
USE TemperatureManag$smartaquarium_db;
SHOW TABLES;
```

## Important Notes

⚠️ **Password**: Your PythonAnywhere login password is the same as your database password
⚠️ **Database Name**: Must include the `$` symbol: `TemperatureManag$smartaquarium_db`
⚠️ **Host**: Use the full hostname: `TemperatureManagement.mysql.pythonanywhere-services.com`

## Testing Connection

After setting password, test on PythonAnywhere bash console:

```bash
python manage.py dbshell
```

Should connect without errors.

---

**Your system is ready for deployment!** 🚀
