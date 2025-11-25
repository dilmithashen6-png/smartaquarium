# Raspberry Pi Setup Guide - Smart Aquarium

Complete guide to set up your Raspberry Pi for the Smart Aquarium control system.

## 🎯 Overview

This guide covers:
1. Raspberry Pi OS setup
2. GPIO configuration for fan/heater control
3. DHT22 temperature/humidity sensor setup
4. Smart Aquarium integration script
5. Automatic startup

## 📋 Prerequisites

- Raspberry Pi 3B+ or newer (or Raspberry Pi Zero)
- Raspbian/Raspberry Pi OS installed
- Internet connection
- SSH access or HDMI monitor + keyboard
- Required hardware:
  - DHT22 temperature/humidity sensor
  - 2x GPIO relay modules (or transistors) for fan/heater control
  - Jumper wires and breadboard

## 🔧 Hardware Wiring

### GPIO Pin Configuration

```
Raspberry Pi GPIO Pinout:

DHT22 Sensor:
- Pin 1 (3.3V) → GPIO 1 (3.3V)
- Pin 2 (Data) → GPIO 4 (with 4.7kΩ resistor to 3.3V)
- Pin 4 (GND) → GPIO 6 (Ground)

Fan Relay (GPIO 17):
- Relay IN → GPIO 17
- Relay+ → 5V
- Relay- → GND
- Relay NO → Fan Live
- Relay COM → Fan Neutral
- Relay NC → Not used

Heater Relay (GPIO 27):
- Relay IN → GPIO 27
- Relay+ → 5V
- Relay- → GND
- Relay NO → Heater Live
- Relay COM → Heater Neutral
- Relay NC → Not used
```

## 📥 Step 1: Update System

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install python3-pip python3-dev -y
```

## 🐍 Step 2: Install Python Packages

```bash
# Required packages
pip3 install requests
pip3 install Adafruit-CircuitPython-DHT
pip3 install RPi.GPIO

# Optional but recommended
pip3 install python-dotenv
```

If you get permission errors, use:
```bash
pip3 install --user requests Adafruit-CircuitPython-DHT RPi.GPIO
```

## 📝 Step 3: Create Configuration File

Create `.env` file in your project directory:

```bash
nano ~/.env
```

Add this content:

```
API_BASE_URL=http://YOUR_SERVER_IP:8000/api
API_KEY=your_rpi_api_key_12345
FAN_PIN=17
HEATER_PIN=27
DHT_PIN=4
SENSOR_INTERVAL=30
DEBUG=False
```

Replace:
- `YOUR_SERVER_IP` with your web server IP/domain
- `your_rpi_api_key_12345` with the API key from settings.py

## 🌡️ Step 4: Create Control Script

Create `aquarium_controller.py`:

```python
#!/usr/bin/env python3
"""
Smart Aquarium Raspberry Pi Controller
Monitors temperature and controls fan/heater
"""

import os
import sys
import time
import json
import logging
import signal
import requests
import RPi.GPIO as GPIO
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000/api')
API_KEY = os.getenv('API_KEY', 'your_rpi_api_key_12345')
FAN_PIN = int(os.getenv('FAN_PIN', 17))
HEATER_PIN = int(os.getenv('HEATER_PIN', 27))
DHT_PIN = int(os.getenv('DHT_PIN', 4))
SENSOR_INTERVAL = int(os.getenv('SENSOR_INTERVAL', 30))
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Logging setup
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('aquarium_controller.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(FAN_PIN, GPIO.OUT)
GPIO.setup(HEATER_PIN, GPIO.OUT)
GPIO.output(FAN_PIN, GPIO.LOW)
GPIO.output(HEATER_PIN, GPIO.LOW)

# Sensor Setup
try:
    import board
    import adafruit_dht
    dht_device = adafruit_dht.DHT22(board.D4)
    logger.info(f"DHT22 sensor initialized on GPIO {DHT_PIN}")
except Exception as e:
    logger.error(f"Failed to initialize DHT22 sensor: {e}")
    dht_device = None


class AquariumController:
    def __init__(self):
        self.running = True
        self.fan_state = False
        self.heater_state = False
        self.last_setpoint = 25.0
        self.sensor_errors = 0
        self.api_errors = 0
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, sig, frame):
        """Handle shutdown signals"""
        logger.info("Shutdown signal received")
        self.shutdown()
    
    def get_sensor_readings(self):
        """Read temperature and humidity from DHT22"""
        try:
            if dht_device is None:
                logger.warning("DHT device not available")
                return None, None
            
            temperature = dht_device.temperature
            humidity = dht_device.humidity
            
            if temperature is None or humidity is None:
                self.sensor_errors += 1
                logger.warning(f"Invalid sensor reading (errors: {self.sensor_errors})")
                return None, None
            
            self.sensor_errors = 0
            return temperature, humidity
        
        except RuntimeError as e:
            self.sensor_errors += 1
            if self.sensor_errors % 10 == 0:
                logger.warning(f"Sensor read error: {e} (errors: {self.sensor_errors})")
            return None, None
        except Exception as e:
            self.sensor_errors += 1
            logger.error(f"Unexpected sensor error: {e}")
            return None, None
    
    def submit_sensor_data(self, temperature, humidity):
        """Send sensor data to web server"""
        try:
            data = {
                "temperature": temperature,
                "humidity": humidity,
                "api_key": API_KEY
            }
            
            response = requests.post(
                f"{API_BASE_URL}/sensor-data/",
                json=data,
                timeout=5
            )
            
            if response.status_code == 201:
                logger.debug(f"Data submitted: {temperature}°C, {humidity}%")
                self.api_errors = 0
                return True
            else:
                self.api_errors += 1
                logger.warning(f"API returned {response.status_code}: {response.text}")
                return False
        
        except requests.exceptions.Timeout:
            self.api_errors += 1
            logger.warning(f"API timeout (errors: {self.api_errors})")
            return False
        except requests.exceptions.ConnectionError:
            self.api_errors += 1
            if self.api_errors % 5 == 0:
                logger.warning(f"Connection to API failed (errors: {self.api_errors})")
            return False
        except Exception as e:
            self.api_errors += 1
            logger.error(f"Error submitting data: {e}")
            return False
    
    def get_setpoint(self):
        """Get temperature setpoint from server"""
        try:
            response = requests.get(
                f"{API_BASE_URL}/get-setpoint/",
                params={"api_key": API_KEY},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                setpoint = data.get('setpoint_temperature', 25.0)
                self.last_setpoint = setpoint
                logger.debug(f"Setpoint fetched: {setpoint}°C")
                return setpoint
            else:
                logger.warning(f"Failed to get setpoint: {response.status_code}")
                return self.last_setpoint
        
        except Exception as e:
            logger.warning(f"Error fetching setpoint: {e}")
            return self.last_setpoint
    
    def get_device_status(self):
        """Get fan and heater status from server"""
        try:
            response = requests.get(
                f"{API_BASE_URL}/get-device-status/",
                params={"api_key": API_KEY},
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to get device status: {response.status_code}")
                return None
        
        except Exception as e:
            logger.warning(f"Error fetching device status: {e}")
            return None
    
    def set_fan(self, state):
        """Control fan"""
        try:
            GPIO.output(FAN_PIN, GPIO.HIGH if state else GPIO.LOW)
            self.fan_state = state
            logger.info(f"Fan: {'ON' if state else 'OFF'}")
            return True
        except Exception as e:
            logger.error(f"Error controlling fan: {e}")
            return False
    
    def set_heater(self, state):
        """Control heater"""
        try:
            GPIO.output(HEATER_PIN, GPIO.HIGH if state else GPIO.LOW)
            self.heater_state = state
            logger.info(f"Heater: {'ON' if state else 'OFF'}")
            return True
        except Exception as e:
            logger.error(f"Error controlling heater: {e}")
            return False
    
    def update_devices(self):
        """Fetch and apply device status from server"""
        try:
            status = self.get_device_status()
            if status:
                self.set_fan(status.get('fan', {}).get('is_on', False))
                self.set_heater(status.get('heater', {}).get('is_on', False))
        except Exception as e:
            logger.error(f"Error updating devices: {e}")
    
    def log_status(self, temp, humidity):
        """Log current system status"""
        logger.info(
            f"Temp: {temp}°C | "
            f"Humidity: {humidity}% | "
            f"Fan: {'ON' if self.fan_state else 'OFF'} | "
            f"Heater: {'ON' if self.heater_state else 'OFF'} | "
            f"Setpoint: {self.last_setpoint}°C"
        )
    
    def main_loop(self):
        """Main control loop"""
        logger.info("Smart Aquarium Controller started")
        logger.info(f"Configuration: API={API_BASE_URL}, Interval={SENSOR_INTERVAL}s")
        
        loop_count = 0
        
        try:
            while self.running:
                loop_count += 1
                
                # Read sensors
                temp, humidity = self.get_sensor_readings()
                
                if temp is not None and humidity is not None:
                    # Submit data
                    self.submit_sensor_data(temp, humidity)
                    
                    # Get setpoint
                    self.get_setpoint()
                    
                    # Update device states from server
                    self.update_devices()
                    
                    # Log every 10 loops (every 5 minutes with 30s interval)
                    if loop_count % 10 == 0:
                        self.log_status(temp, humidity)
                
                # Wait before next reading
                time.sleep(SENSOR_INTERVAL)
        
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Clean shutdown"""
        logger.info("Shutting down...")
        self.running = False
        
        # Turn off all devices
        self.set_fan(False)
        self.set_heater(False)
        
        # Clean up GPIO
        try:
            GPIO.cleanup()
            logger.info("GPIO cleaned up")
        except Exception as e:
            logger.warning(f"Error cleaning GPIO: {e}")
        
        logger.info("Smart Aquarium Controller stopped")
        sys.exit(0)


def main():
    """Entry point"""
    try:
        controller = AquariumController()
        controller.main_loop()
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

## 🚀 Step 5: Test the Script

```bash
# Make script executable
chmod +x aquarium_controller.py

# Run with debugging
DEBUG=true python3 aquarium_controller.py
```

You should see:
```
INFO - Smart Aquarium Controller started
INFO - Temp: 25.5°C | Humidity: 60% | Fan: OFF | Heater: OFF | Setpoint: 25.0°C
```

## 🔄 Step 6: Auto-start on Boot

### Option A: Using systemd (Recommended)

Create service file:
```bash
sudo nano /etc/systemd/system/aquarium.service
```

Add content:
```ini
[Unit]
Description=Smart Aquarium Controller
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/smartaquarium
ExecStart=/usr/bin/python3 /home/pi/smartaquarium/aquarium_controller.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable aquarium.service
sudo systemctl start aquarium.service
```

Check status:
```bash
sudo systemctl status aquarium.service
```

View logs:
```bash
sudo journalctl -u aquarium.service -f
```

### Option B: Using crontab

```bash
crontab -e
```

Add this line:
```
@reboot /usr/bin/python3 /home/pi/smartaquarium/aquarium_controller.py &
```

## 📊 Monitoring

### View Live Logs

```bash
# Using systemd
sudo journalctl -u aquarium.service -f

# Or local log file
tail -f aquarium_controller.log
```

### Check System Health

```bash
# CPU/Memory usage
top

# Network connectivity
ping google.com

# Test API connection
curl "http://YOUR_SERVER_IP:8000/api/get-setpoint/?api_key=your_key"
```

## 🧪 Testing

### Test Sensor Reading

```python
import board
import adafruit_dht

dht_device = adafruit_dht.DHT22(board.D4)
print(f"Temp: {dht_device.temperature}°C")
print(f"Humidity: {dht_device.humidity}%")
```

### Test GPIO

```python
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)

GPIO.output(17, GPIO.HIGH)
time.sleep(1)
GPIO.output(17, GPIO.LOW)

GPIO.cleanup()
```

### Test API Connection

```bash
# Test API
curl -X POST http://YOUR_SERVER_IP:8000/api/api/sensor-data/ \
  -H "Content-Type: application/json" \
  -d '{"temperature": 25.5, "humidity": 60.0, "api_key": "your_key"}'
```

## 🔒 Security Tips

1. **Change API Key**: Use strong random key
2. **Use HTTPS**: Set up SSL certificate for your server
3. **Restrict Network**: Use firewall to limit API access
4. **Secure SSH**: Change default Pi password
   ```bash
   passwd
   ```

## 🐛 Troubleshooting

### DHT22 Not Reading
```bash
# Check GPIO pin is correct
# Verify 4.7kΩ pullup resistor is connected
# Try different GPIO pin in .env file
```

### API Connection Failed
```bash
# Test connection
ping YOUR_SERVER_IP
curl http://YOUR_SERVER_IP:8000/

# Check API key matches
# Verify URL is correct in .env
```

### Service Not Starting
```bash
# Check service status
sudo systemctl status aquarium.service

# View error logs
sudo journalctl -u aquarium.service -n 50

# Manually run script
python3 aquarium_controller.py
```

### GPIO Permission Denied
```bash
# Add pi user to gpio group
sudo usermod -a -G gpio pi

# Log out and back in
```

## 📦 File Structure

```
smartaquarium/
├── aquarium_controller.py  (Main script)
├── .env                     (Configuration)
├── aquarium_controller.log  (Auto-created)
└── README.md               (This file)
```

## 🎯 Next Steps

1. ✅ Complete hardware setup
2. ✅ Install Python packages
3. ✅ Create .env configuration
4. ✅ Test aquarium_controller.py manually
5. ✅ Set up systemd service for auto-start
6. ✅ Verify logs in web dashboard

## 📞 Support

- **Raspberry Pi Docs**: https://www.raspberrypi.org/documentation/
- **GPIO Guide**: https://www.raspberrypi.org/documentation/usage/gpio/
- **DHT22 Library**: https://github.com/adafruit/Adafruit_CircuitPython_DHT

---

**Your Raspberry Pi Smart Aquarium controller is ready!** 🐠🌡️
