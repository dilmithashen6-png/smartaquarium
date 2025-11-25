# Smart Aquarium Temperature Control System

A complete web-based system for monitoring and controlling aquarium temperature using Django, MySQL, and Raspberry Pi integration.

## Features

### 🌡️ Core Features
- **Real-time Temperature & Humidity Monitoring**: Display live sensor readings
- **Device Control**: Toggle Fan and Heater on/off remotely
- **Temperature Setpoint Control**: Admin can set target temperature for automatic control
- **Data Logging**: All sensor readings stored with timestamps in MySQL
- **Public Dashboard**: View-only dashboard accessible without login
- **Admin Dashboard**: Full control panel with authentication
- **Data History**: View all historical sensor readings with pagination

### 🔐 Security
- Admin login with username/password authentication
- Session-based authentication
- API key validation for Raspberry Pi communication
- CSRF protection on all forms

### 📡 Raspberry Pi Integration
- REST API endpoints for sensor data submission
- Endpoints to fetch current setpoint and device status
- Support for any sensor sending JSON data

## System Architecture

```
Frontend (HTML/CSS/JavaScript)
        ↓
Django Web Server
        ↓
MySQL Database
        ↓
Raspberry Pi (Sensor & Device Control)
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- MySQL Server
- pip (Python package manager)
- Raspberry Pi (optional, for sensor integration)

### Step 1: Install Required Python Packages

```bash
pip install django
pip install django-rest-framework
pip install mysqlclient
```

**Note**: On Windows, you might need to install MySQL C libraries first. Download from MySQL website or use:
```bash
pip install mysql-connector-python
```

### Step 2: Configure MySQL Database

1. Create MySQL database and user:

```sql
CREATE DATABASE smartaquarium_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'aquarium_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON smartaquarium_db.* TO 'aquarium_user'@'localhost';
FLUSH PRIVILEGES;
```

### Step 3: Update Django Settings

Edit `smartAquarium/settings.py` and update the database credentials:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'smartaquarium_db',
        'USER': 'aquarium_user',
        'PASSWORD': 'your_secure_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### Step 4: Create Database Tables

Run migrations:

```bash
python manage.py migrate
```

### Step 5: Create Admin User

```bash
python manage.py createsuperuser
```

Follow the prompts to create your admin account.

### Step 6: Update API Key (Optional)

Edit `api/views.py` and change the API key:

```python
VALID_API_KEY = 'your_rpi_api_key_12345'  # Change this to a secure key
```

### Step 7: Run Development Server

```bash
python manage.py runserver
```

Server will be available at `http://localhost:8000`

## URLs & Endpoints

### Web Interface
- `http://localhost:8000/` - Home page
- `http://localhost:8000/api/public-dashboard/` - Public dashboard (no login required)
- `http://localhost:8000/api/login/` - Admin login page
- `http://localhost:8000/api/dashboard/` - Admin dashboard (login required)
- `http://localhost:8000/api/history/` - Sensor data history (login required)

### REST API Endpoints (for Raspberry Pi)

#### 1. Submit Sensor Data
**POST** `/api/api/sensor-data/`

Request body:
```json
{
  "temperature": 25.5,
  "humidity": 60.0,
  "api_key": "your_rpi_api_key_12345"
}
```

Response:
```json
{
  "success": true,
  "message": "Sensor data recorded",
  "data_id": 1,
  "timestamp": "2024-01-15T10:30:45.123456Z"
}
```

#### 2. Get Temperature Setpoint
**GET** `/api/api/get-setpoint/?api_key=your_rpi_api_key_12345`

Response:
```json
{
  "setpoint_temperature": 25.0,
  "updated_at": "2024-01-15T10:30:45.123456Z"
}
```

#### 3. Get Device Status
**GET** `/api/api/get-device-status/?api_key=your_rpi_api_key_12345`

Response:
```json
{
  "fan": {
    "is_on": false,
    "last_updated": "2024-01-15T10:30:45.123456Z"
  },
  "heater": {
    "is_on": true,
    "last_updated": "2024-01-15T10:30:45.123456Z"
  }
}
```

#### 4. Get Latest Sensor Reading
**GET** `/api/api/latest-sensor/?api_key=your_rpi_api_key_12345`

Response:
```json
{
  "temperature": 25.5,
  "humidity": 60.0,
  "timestamp": "2024-01-15T10:30:45.123456Z"
}
```

## Raspberry Pi Integration Example

### Python Script for Raspberry Pi

Create a file `raspi_control.py`:

```python
import requests
import json
import time
from datetime import datetime
import board
import adafruit_dht
import RPi.GPIO as GPIO

# Configuration
API_BASE_URL = "http://your_server_ip:8000/api"
API_KEY = "your_rpi_api_key_12345"

# GPIO Setup
FAN_PIN = 17
HEATER_PIN = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(FAN_PIN, GPIO.OUT)
GPIO.setup(HEATER_PIN, GPIO.OUT)

# Sensor Setup (DHT22)
dht_device = adafruit_dht.DHT22(board.D4)

def get_sensor_readings():
    """Read temperature and humidity from DHT22"""
    try:
        temperature = dht_device.temperature
        humidity = dht_device.humidity
        return temperature, humidity
    except Exception as e:
        print(f"Sensor error: {e}")
        return None, None

def submit_sensor_data(temperature, humidity):
    """Send sensor data to web server"""
    try:
        data = {
            "temperature": temperature,
            "humidity": humidity,
            "api_key": API_KEY
        }
        response = requests.post(
            f"{API_BASE_URL}/sensor-data/",
            json=data
        )
        print(f"Data submitted: {response.json()}")
    except Exception as e:
        print(f"Error submitting data: {e}")

def get_setpoint():
    """Get temperature setpoint from server"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/get-setpoint/",
            params={"api_key": API_KEY}
        )
        return response.json()['setpoint_temperature']
    except Exception as e:
        print(f"Error getting setpoint: {e}")
        return 25.0

def get_device_status():
    """Get fan and heater status from server"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/get-device-status/",
            params={"api_key": API_KEY}
        )
        return response.json()
    except Exception as e:
        print(f"Error getting device status: {e}")
        return None

def control_fan(state):
    """Control fan (True=ON, False=OFF)"""
    GPIO.output(FAN_PIN, GPIO.HIGH if state else GPIO.LOW)
    print(f"Fan: {'ON' if state else 'OFF'}")

def control_heater(state):
    """Control heater (True=ON, False=OFF)"""
    GPIO.output(HEATER_PIN, GPIO.HIGH if state else GPIO.LOW)
    print(f"Heater: {'ON' if state else 'OFF'}")

def main():
    """Main control loop"""
    print("Smart Aquarium Raspberry Pi Controller Started")
    
    try:
        while True:
            # Read sensors
            temp, humidity = get_sensor_readings()
            
            if temp is not None and humidity is not None:
                print(f"\n[{datetime.now()}] Temp: {temp}°C, Humidity: {humidity}%")
                
                # Submit data to server
                submit_sensor_data(temp, humidity)
                
                # Get setpoint from server
                setpoint = get_setpoint()
                print(f"Setpoint: {setpoint}°C")
                
                # Get device status from server
                status = get_device_status()
                if status:
                    control_fan(status['fan']['is_on'])
                    control_heater(status['heater']['is_on'])
                
                # Simple temperature control logic (optional)
                # if temp < setpoint - 1:
                #     control_heater(True)
                # elif temp > setpoint + 1:
                #     control_fan(True)
            
            # Wait before next reading (every 30 seconds)
            time.sleep(30)
    
    except KeyboardInterrupt:
        print("\nShutdown...")
        GPIO.cleanup()

if __name__ == "__main__":
    main()
```

### Dependencies for Raspberry Pi

```bash
pip install requests
pip install adafruit-circuitpython-dht
pip install RPi.GPIO
```

## Production Deployment (PythonAnywhere)

1. **Upload your code** to PythonAnywhere web console
2. **Install packages** in PythonAnywhere bash console:
   ```bash
   pip install --user django django-rest-framework mysqlclient
   ```

3. **Configure Web App**:
   - Create web app with Python 3.8+
   - Set WSGI file to point to `smartAquarium/wsgi.py`

4. **Database**:
   - Use PythonAnywhere MySQL or external MySQL service

5. **Update settings.py**:
   - Set `DEBUG = False`
   - Add your domain to `ALLOWED_HOSTS`
   - Configure `STATIC_URL` for collectstatic

6. **Collect static files**:
   ```bash
   python manage.py collectstatic --noinput
   ```

7. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

## Database Schema

### SensorData Model
```
- id (Primary Key)
- temperature (Float)
- humidity (Float)
- timestamp (DateTime) - Auto-generated
```

### DeviceControl Model
```
- id (Primary Key)
- device (CharField: 'fan' or 'heater')
- is_on (Boolean)
- last_updated (DateTime) - Auto-updated
```

### TemperatureSetpoint Model
```
- id (Primary Key)
- setpoint_temperature (Float)
- created_by (ForeignKey to User)
- created_at (DateTime) - Auto-generated
- updated_at (DateTime) - Auto-updated
- is_active (Boolean)
```

## Troubleshooting

### Database Connection Error
- Verify MySQL is running
- Check credentials in `settings.py`
- Ensure database exists

### Templates Not Found
- Verify `templates` folder exists in project root
- Check `TEMPLATES` setting in `settings.py`

### Static Files Not Loading
- Run `python manage.py collectstatic` (production)
- Check `STATIC_URL` and `STATICFILES_DIRS` in settings

### API Key Errors
- Update API key in `api/views.py`
- Match key in Raspberry Pi script
- Ensure correct format in requests

## Security Considerations

⚠️ **Important for Production**:

1. Change `SECRET_KEY` in settings.py
2. Set `DEBUG = False`
3. Use HTTPS (SSL/TLS)
4. Use strong passwords for database and admin
5. Update API key to a strong random value
6. Consider adding rate limiting
7. Use environment variables for sensitive data

## Support & Documentation

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [MySQL Documentation](https://dev.mysql.com/doc/)

## License

This project is provided as-is for educational and personal use.

---

**Created**: 2024
**Version**: 1.0
**Status**: Active Development
