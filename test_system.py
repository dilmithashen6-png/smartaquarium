#!/usr/bin/env python
"""
Smart Aquarium System Tester
Tests all API endpoints and database connectivity
"""

import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartAquarium.settings')
django.setup()

from django.test.utils import get_runner
from django.db import connection
from api.models import SensorData, DeviceControl, TemperatureSetpoint
from django.contrib.auth.models import User


class AquariumSystemTester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0

    def test_database_connection(self):
        """Test MySQL database connection"""
        print("\n[TEST 1] Database Connection")
        try:
            connection.ensure_connection()
            print("✓ Database connection successful")
            self.passed += 1
            return True
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            self.failed += 1
            return False

    def test_models(self):
        """Test database models"""
        print("\n[TEST 2] Database Models")
        try:
            # Check SensorData table
            count = SensorData.objects.count()
            print(f"✓ SensorData table exists ({count} records)")
            
            # Check DeviceControl table
            fan_exists = DeviceControl.objects.filter(device='fan').exists()
            heater_exists = DeviceControl.objects.filter(device='heater').exists()
            
            if fan_exists:
                print("✓ Fan device control exists")
            else:
                print("⚠ Fan device control not found (will be created on first use)")
                self.warnings += 1
            
            if heater_exists:
                print("✓ Heater device control exists")
            else:
                print("⚠ Heater device control not found (will be created on first use)")
                self.warnings += 1
            
            # Check TemperatureSetpoint
            setpoint = TemperatureSetpoint.objects.filter(is_active=True).first()
            if setpoint:
                print(f"✓ Temperature setpoint exists: {setpoint.setpoint_temperature}°C")
            else:
                print("⚠ No active temperature setpoint (will be created on first admin save)")
                self.warnings += 1
            
            self.passed += 1
            return True
        except Exception as e:
            print(f"✗ Model test failed: {e}")
            self.failed += 1
            return False

    def test_admin_user(self):
        """Check if admin user exists"""
        print("\n[TEST 3] Admin User")
        try:
            admin_count = User.objects.filter(is_superuser=True).count()
            if admin_count > 0:
                users = User.objects.filter(is_superuser=True).values_list('username', flat=True)
                print(f"✓ Admin user(s) found: {', '.join(users)}")
                self.passed += 1
                return True
            else:
                print("⚠ No superuser found")
                print("  Run: python manage.py createsuperuser")
                self.warnings += 1
                return True
        except Exception as e:
            print(f"✗ Admin user check failed: {e}")
            self.failed += 1
            return False

    def test_settings(self):
        """Check critical settings"""
        print("\n[TEST 4] Django Settings")
        issues = []
        
        # Check DEBUG
        if settings.DEBUG:
            issues.append("⚠ DEBUG is True (should be False in production)")
        else:
            print("✓ DEBUG is False (production mode)")
        
        # Check ALLOWED_HOSTS
        if not settings.ALLOWED_HOSTS or settings.ALLOWED_HOSTS == ['*']:
            issues.append("⚠ ALLOWED_HOSTS not properly configured")
        else:
            print(f"✓ ALLOWED_HOSTS configured: {settings.ALLOWED_HOSTS}")
        
        # Check Database
        db_engine = settings.DATABASES['default']['ENGINE']
        db_name = settings.DATABASES['default']['NAME']
        
        if 'mysql' in db_engine.lower():
            print(f"✓ Database: MySQL ({db_name})")
        else:
            issues.append(f"⚠ Database is {db_engine}, MySQL recommended")
        
        # Check SECRET_KEY
        if 'insecure' in settings.SECRET_KEY.lower():
            issues.append("⚠ Default SECRET_KEY detected (change in production)")
        else:
            print("✓ SECRET_KEY appears to be custom")
        
        if issues:
            for issue in issues:
                print(issue)
                self.warnings += 1
        
        self.passed += 1
        return True

    def test_static_files(self):
        """Check static files configuration"""
        print("\n[TEST 5] Static Files")
        try:
            static_url = settings.STATIC_URL
            print(f"✓ STATIC_URL: {static_url}")
            
            if hasattr(settings, 'STATICFILES_DIRS'):
                print(f"✓ STATICFILES_DIRS: {settings.STATICFILES_DIRS}")
            
            self.passed += 1
            return True
        except Exception as e:
            print(f"✗ Static files check failed: {e}")
            self.failed += 1
            return False

    def test_sample_data_insertion(self):
        """Test inserting sample sensor data"""
        print("\n[TEST 6] Sample Data Insertion")
        try:
            # Create sample sensor data
            sensor = SensorData.objects.create(
                temperature=25.5,
                humidity=60.0
            )
            print(f"✓ Created sample sensor data (ID: {sensor.id})")
            
            # Retrieve it
            retrieved = SensorData.objects.get(id=sensor.id)
            print(f"✓ Retrieved sensor data: {retrieved.temperature}°C, {retrieved.humidity}%")
            
            # Clean up
            sensor.delete()
            print("✓ Cleanup successful")
            
            self.passed += 1
            return True
        except Exception as e:
            print(f"✗ Sample data insertion failed: {e}")
            self.failed += 1
            return False

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*50)
        print("TEST SUMMARY")
        print("="*50)
        print(f"✓ Passed: {self.passed}")
        print(f"✗ Failed: {self.failed}")
        print(f"⚠ Warnings: {self.warnings}")
        print("="*50)
        
        if self.failed == 0:
            print("\n✓ All tests passed!")
            if self.warnings > 0:
                print(f"⚠ {self.warnings} warning(s) - review above")
        else:
            print(f"\n✗ {self.failed} test(s) failed - see above for details")
        
        return self.failed == 0

    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*50)
        print("SMART AQUARIUM SYSTEM TEST")
        print("="*50)
        
        self.test_database_connection()
        self.test_models()
        self.test_admin_user()
        self.test_settings()
        self.test_static_files()
        self.test_sample_data_insertion()
        
        return self.print_summary()


def main():
    """Main test runner"""
    tester = AquariumSystemTester()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
