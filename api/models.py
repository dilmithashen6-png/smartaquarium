from django.db import models
from django.contrib.auth.models import User

class SensorData(models.Model):
    """Model to store sensor readings (temperature and humidity)"""
    temperature = models.FloatField()
    humidity = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = "Sensor Data"
    
    def __str__(self):
        return f"Temp: {self.temperature}°C, Humidity: {self.humidity}% - {self.timestamp}"


class DeviceControl(models.Model):
    """Model to store device control states (fan and heater)"""
    DEVICE_CHOICES = [
        ('fan', 'Fan'),
        ('heater', 'Heater'),
    ]
    
    device = models.CharField(max_length=10, choices=DEVICE_CHOICES)
    is_on = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('device',)
    
    def __str__(self):
        status = "ON" if self.is_on else "OFF"
        return f"{self.device.upper()} - {status}"


class TemperatureSetpoint(models.Model):
    """Model to store temperature setpoint for control"""
    setpoint_temperature = models.FloatField(default=25.0)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Setpoint: {self.setpoint_temperature}°C"
