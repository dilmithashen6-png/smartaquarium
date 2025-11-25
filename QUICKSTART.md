# Smart Aquarium - Quick Start Guide

## ⚡ 5-Minute Setup

### Prerequisites
- Python 3.8+ installed
- MySQL Server installed and running
- Internet connection

### Step 1: Install Dependencies (1 min)
```bash
pip install -r requirements.txt
```

### Step 2: Configure Database (2 min)

#### On MySQL Console:
```sql
CREATE DATABASE smartaquarium_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'aquarium_user'@'localhost' IDENTIFIED BY 'password123';
GRANT ALL PRIVILEGES ON smartaquarium_db.* TO 'aquarium_user'@'localhost';
FLUSH PRIVILEGES;
```

#### Update `smartAquarium/settings.py`:
Find this section:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'smartaquarium_db',
        'USER': 'aquarium_user',
        'PASSWORD': 'password123',  # <-- Change to your MySQL password
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### Step 3: Run Migrations (1 min)
```bash
python manage.py migrate
```

### Step 4: Create Admin User (1 min)
```bash
python manage.py createsuperuser
```

Follow the prompts to create username/password.

### Step 5: Start Server (1 min)
```bash
python manage.py runserver
```

## ✅ Verify Installation

Open your browser and visit:

1. **Public Dashboard** (No login): `http://localhost:8000/api/public-dashboard/`
2. **Admin Dashboard** (With login): `http://localhost:8000/api/dashboard/`
3. **Django Admin**: `http://localhost:8000/admin/`

Login with credentials you created in Step 4.

## 🎮 First Time Usage

### 1. Submit Sensor Data (Test API)

```bash
curl -X POST http://localhost:8000/api/api/sensor-data/ \
  -H "Content-Type: application/json" \
  -d '{
    "temperature": 25.5,
    "humidity": 60.0,
    "api_key": "your_rpi_api_key_12345"
  }'
```

### 2. View Dashboard

Visit: `http://localhost:8000/api/public-dashboard/`

You should see the temperature and humidity readings you submitted.

### 3. Control Devices

Login to admin dashboard: `http://localhost:8000/api/dashboard/`

- Set temperature setpoint
- Turn fan ON/OFF
- Turn heater ON/OFF
- View data history

## 📱 Raspberry Pi Integration

### 1. Update API Key (Security)

Edit `api/views.py` and find:
```python
VALID_API_KEY = 'your_rpi_api_key_12345'
```

Change to a strong key:
```python
VALID_API_KEY = 'sk_live_abc123xyz789'
```

### 2. Copy RPi Script

Copy this script to your Raspberry Pi as `raspi_control.py`:

```python
import requests
import time
from datetime import datetime

# Configuration
API_BASE_URL = "http://YOUR_SERVER_IP:8000/api"
API_KEY = "sk_live_abc123xyz789"  # Match your settings.py key

def submit_sensor_data(temp, humidity):
    try:
        data = {
            "temperature": temp,
            "humidity": humidity,
            "api_key": API_KEY
        }
        response = requests.post(
            f"{API_BASE_URL}/sensor-data/",
            json=data
        )
        print(f"✓ Data sent: {response.json()}")
    except Exception as e:
        print(f"✗ Error: {e}")

def get_device_status():
    try:
        response = requests.get(
            f"{API_BASE_URL}/get-device-status/",
            params={"api_key": API_KEY}
        )
        data = response.json()
        print(f"Fan: {'ON' if data['fan']['is_on'] else 'OFF'}")
        print(f"Heater: {'ON' if data['heater']['is_on'] else 'OFF'}")
    except Exception as e:
        print(f"✗ Error: {e}")

# Main loop
print("Starting sensor readings...")
while True:
    temp = 25.5  # Replace with actual sensor reading
    humidity = 60.0  # Replace with actual humidity reading
    
    print(f"\n[{datetime.now()}] Temp: {temp}°C, Humidity: {humidity}%")
    submit_sensor_data(temp, humidity)
    get_device_status()
    
    time.sleep(30)  # Read every 30 seconds
```

### 3. Install Dependencies on RPi

```bash
pip install requests
```

For sensor support (DHT22):
```bash
pip install adafruit-circuitpython-dht
```

### 4. Run the Script

```bash
python raspi_control.py
```

## 📊 Available Endpoints

### Web Interface
- `/` - Home page
- `/api/public-dashboard/` - Public monitoring (no login)
- `/api/login/` - Admin login
- `/api/dashboard/` - Admin control panel
- `/api/history/` - Data history (login required)

### REST API (Raspberry Pi)
- `POST /api/api/sensor-data/` - Submit sensor readings
- `GET /api/api/get-setpoint/` - Get temperature setpoint
- `GET /api/api/get-device-status/` - Get fan/heater status
- `GET /api/api/latest-sensor/` - Get latest readings

## 🔧 Common Issues & Solutions

### "ModuleNotFoundError: No module named 'mysqlclient'"
```bash
pip install mysqlclient
```

### "Can't connect to MySQL server"
1. Check MySQL is running
2. Verify username/password in settings.py
3. Create database and user (see Step 2)

### "Static files not loading"
```bash
python manage.py collectstatic
```

### "No data showing on dashboard"
1. Submit test data using curl command above
2. Refresh browser
3. Check database connection

### "API authentication failed"
- Verify API key matches in both files
- Check API key includes quotes
- Ensure JSON format is correct

## 📝 Next Steps

1. ✅ Complete quick start above
2. 📖 Read CONFIGURATION.md for detailed settings
3. 🐍 Set up Raspberry Pi integration
4. 🌐 Deploy to PythonAnywhere (production)
5. 🔒 Update security settings (see CONFIGURATION.md)

## 🚀 Production Deployment

See `CONFIGURATION.md` section "Raspberry Pi Configuration" and README.md section "Production Deployment (PythonAnywhere)"

## 📞 Support

- **Django Docs**: https://docs.djangoproject.com/
- **REST Framework**: https://www.django-rest-framework.org/
- **MySQL Docs**: https://dev.mysql.com/doc/

---

**Happy monitoring! 🐠**
