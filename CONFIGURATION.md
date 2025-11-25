# Smart Aquarium - Configuration Guide

## Overview
This guide walks you through configuring the Smart Aquarium control system for your environment.

## 1. Database Configuration

### MySQL Setup

#### On Windows:
1. Download MySQL Community Server from: https://dev.mysql.com/downloads/mysql/
2. Install MySQL Server
3. Open MySQL Command Line Client or use MySQL Workbench
4. Run the following SQL commands:

```sql
-- Create database
CREATE DATABASE smartaquarium_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user
CREATE USER 'aquarium_user'@'localhost' IDENTIFIED BY 'your_secure_password_123';

-- Grant privileges
GRANT ALL PRIVILEGES ON smartaquarium_db.* TO 'aquarium_user'@'localhost';
FLUSH PRIVILEGES;
```

#### On Linux/Mac:
```bash
# Log into MySQL
mysql -u root -p

# In MySQL console
CREATE DATABASE smartaquarium_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'aquarium_user'@'localhost' IDENTIFIED BY 'your_secure_password_123';
GRANT ALL PRIVILEGES ON smartaquarium_db.* TO 'aquarium_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Update Django Settings

Edit `smartAquarium/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'smartaquarium_db',        # Database name
        'USER': 'aquarium_user',           # MySQL username
        'PASSWORD': 'your_secure_password_123',  # MySQL password
        'HOST': 'localhost',               # MySQL host (localhost for local)
        'PORT': '3306',                    # MySQL port (default 3306)
    }
}
```

## 2. API Key Configuration

### Generate Secure API Key

Edit `api/views.py` and update this line:

```python
VALID_API_KEY = 'your_rpi_api_key_12345'
```

**Recommendation**: Use a strong random key generated with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Then use that key. For example:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 3. Django Secret Key (Production Only)

For production, change the SECRET_KEY in `smartAquarium/settings.py`:

```python
SECRET_KEY = 'django-insecure-YOUR_NEW_SECRET_KEY_HERE'
```

Generate new secret key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 4. Allowed Hosts Configuration

Edit `smartAquarium/settings.py`:

```python
# For development
ALLOWED_HOSTS = ['*']

# For production (PythonAnywhere example)
ALLOWED_HOSTS = ['yourusername.pythonanywhere.com']

# For local + remote
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'yourusername.pythonanywhere.com', 'your_domain.com']
```

## 5. Static Files Configuration

### For Development
Default configuration works:
```python
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static/')]
```

### For Production (PythonAnywhere)
```python
STATIC_URL = '/static/'
STATIC_ROOT = '/home/yourusername/smartaquarium/static'

# Remove or comment out STATICFILES_DIRS for production
# STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static/')]
```

Then run:
```bash
python manage.py collectstatic
```

## 6. Environment Variables (Optional but Recommended)

Create `.env` file in project root:

```
DEBUG=False
SECRET_KEY=your_secret_key_here
DB_NAME=smartaquarium_db
DB_USER=aquarium_user
DB_PASSWORD=your_password_here
DB_HOST=localhost
API_KEY=your_rpi_api_key_here
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
```

Update `settings.py` to use environment variables:

```python
import os
from dotenv import load_dotenv

load_dotenv()

DEBUG = os.getenv('DEBUG', 'False') == 'True'
SECRET_KEY = os.getenv('SECRET_KEY', 'default-key')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': '3306',
    }
}

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')
```

Install python-dotenv:
```bash
pip install python-dotenv
```

## 7. Email Configuration (Optional)

For sending notifications, edit `settings.py`:

```python
# Using Gmail
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your_email@gmail.com'
EMAIL_HOST_PASSWORD = 'your_app_password'
DEFAULT_FROM_EMAIL = 'your_email@gmail.com'
```

## 8. Logging Configuration (Optional)

Add to `settings.py` for debugging:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'debug.log'),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

## 9. Raspberry Pi Configuration

### Update RPi Script Settings

Edit `raspi_control.py` on your Raspberry Pi:

```python
# Configuration
API_BASE_URL = "http://your_server_ip:8000/api"  # Update to your server
API_KEY = "your_rpi_api_key_12345"  # Must match web server API key

# GPIO Pin Settings (adjust to your setup)
FAN_PIN = 17
HEATER_PIN = 27

# Sensor GPIO Pin
DHT_PIN = 4  # D4 on Raspberry Pi
```

## 10. Running the Application

### Development Mode

```bash
# Navigate to project directory
cd smartAquarium

# Run migrations (if not done)
python manage.py migrate

# Create superuser (if not done)
python manage.py createsuperuser

# Start server
python manage.py runserver
```

Access at: `http://localhost:8000`

### Production Mode (PythonAnywhere)

1. Set DEBUG = False in settings.py
2. Update ALLOWED_HOSTS
3. Configure static files:
   ```bash
   python manage.py collectstatic --noinput
   ```
4. Set up web app in PythonAnywhere dashboard
5. Reload web app

## 11. Testing the System

### Test Database Connection
```bash
python manage.py shell
>>> from django.db import connection
>>> connection.ensure_connection()
# Should complete without error
```

### Test API Endpoints
```bash
# Test sensor data submission
curl -X POST http://localhost:8000/api/api/sensor-data/ \
  -H "Content-Type: application/json" \
  -d '{"temperature": 25.5, "humidity": 60.0, "api_key": "your_rpi_api_key_12345"}'

# Test get setpoint
curl "http://localhost:8000/api/api/get-setpoint/?api_key=your_rpi_api_key_12345"

# Test get device status
curl "http://localhost:8000/api/api/get-device-status/?api_key=your_rpi_api_key_12345"
```

## 12. Troubleshooting

### Error: "No module named 'mysqlclient'"
```bash
pip install mysqlclient
```

On Windows, you might need to install MySQL C development libraries first.

### Error: "Can't connect to MySQL server"
- Verify MySQL is running
- Check username and password
- Check host and port
- Verify database exists

### Static files not loading
```bash
python manage.py collectstatic --clear
python manage.py runserver
```

### CSRF validation failed
- Clear browser cookies
- Verify CSRF token in form
- Check CSRF middleware is enabled

### API key authentication failed
- Update API key in both `api/views.py` and Raspberry Pi script
- Make sure the keys match exactly
- Verify headers are correct

## Security Checklist

- [ ] Change SECRET_KEY from default
- [ ] Set DEBUG = False for production
- [ ] Update ALLOWED_HOSTS
- [ ] Change database password
- [ ] Change API key to strong random value
- [ ] Use HTTPS/SSL in production
- [ ] Create strong admin password
- [ ] Remove default Django admin path (optional)
- [ ] Set up firewall rules
- [ ] Enable HTTPS for API calls from Raspberry Pi

## Next Steps

1. Complete configuration following this guide
2. Run setup script: `setup.bat` (Windows) or `setup.sh` (Linux/Mac)
3. Create admin user: `python manage.py createsuperuser`
4. Test in browser: `http://localhost:8000`
5. Configure Raspberry Pi for API integration
6. Deploy to production (PythonAnywhere)

---

For more help, see README.md or Django documentation at: https://docs.djangoproject.com/
