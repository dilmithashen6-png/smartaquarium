from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import SensorData, DeviceControl, TemperatureSetpoint
import json
from django.core.paginator import Paginator
from datetime import timedelta
from django.utils import timezone

# ==================== Authentication Views ====================

def login_view(request):
    """Admin login page"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    
    return render(request, 'login.html')


@login_required(login_url='login')
def logout_view(request):
    """Logout user"""
    logout(request)
    return redirect('login')


# ==================== Dashboard Views ====================

@login_required(login_url='login')
def admin_dashboard(request):
    """Admin control panel dashboard"""
    latest_sensor = SensorData.objects.first()
    devices = DeviceControl.objects.all()
    setpoint = TemperatureSetpoint.objects.filter(is_active=True).first()
    
    context = {
        'latest_sensor': latest_sensor,
        'devices': devices,
        'setpoint': setpoint,
    }
    return render(request, 'admin_dashboard.html', context)


def public_dashboard(request):
    """Public dashboard (read-only, no login required)"""
    latest_sensor = SensorData.objects.first()
    devices = DeviceControl.objects.all()
    setpoint = TemperatureSetpoint.objects.filter(is_active=True).first()
    
    context = {
        'latest_sensor': latest_sensor,
        'devices': devices,
        'setpoint': setpoint,
    }
    return render(request, 'public_dashboard.html', context)


@login_required(login_url='login')
def data_history(request):
    """View historical sensor data"""
    sensor_data = SensorData.objects.all()
    
    # Pagination
    paginator = Paginator(sensor_data, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'data_history.html', context)


# ==================== Admin Control Views ====================

@login_required(login_url='login')
@require_http_methods(["POST"])
def update_setpoint(request):
    """Update temperature setpoint"""
    try:
        data = json.loads(request.body)
        new_setpoint = float(data.get('setpoint', 25.0))
        
        # Get or create active setpoint
        setpoint, created = TemperatureSetpoint.objects.get_or_create(
            is_active=True,
            defaults={'setpoint_temperature': new_setpoint, 'created_by': request.user}
        )
        
        setpoint.setpoint_temperature = new_setpoint
        setpoint.created_by = request.user
        setpoint.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Setpoint updated to {new_setpoint}°C',
            'setpoint': new_setpoint
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required(login_url='login')
@require_http_methods(["POST"])
def control_device(request):
    """Control fan or heater"""
    try:
        data = json.loads(request.body)
        device = data.get('device')  # 'fan' or 'heater'
        action = data.get('action')  # 'on' or 'off'
        
        if device not in ['fan', 'heater']:
            return JsonResponse({
                'success': False,
                'error': 'Invalid device'
            }, status=400)
        
        device_obj, created = DeviceControl.objects.get_or_create(
            device=device,
            defaults={'is_on': False}
        )
        
        device_obj.is_on = (action == 'on')
        device_obj.save()
        
        return JsonResponse({
            'success': True,
            'message': f'{device.capitalize()} turned {action.upper()}',
            'device': device,
            'status': device_obj.is_on
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


# ==================== REST API Endpoints for Raspberry Pi ====================

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def api_sensor_data(request):
    """
    API endpoint for Raspberry Pi to send sensor data
    Expected POST data: {"temperature": 25.5, "humidity": 60.0, "api_key": "your_key"}
    """
    if request.method == 'POST':
        try:
            temperature = request.data.get('temperature')
            humidity = request.data.get('humidity')
            api_key = request.data.get('api_key', '')
            
            # Basic API key validation (implement your own security)
            VALID_API_KEY = 'your_rpi_api_key_12345'
            if api_key != VALID_API_KEY:
                return Response({
                    'error': 'Invalid API key'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            if temperature is None or humidity is None:
                return Response({
                    'error': 'Missing temperature or humidity'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            sensor_data = SensorData.objects.create(
                temperature=float(temperature),
                humidity=float(humidity)
            )
            
            return Response({
                'success': True,
                'message': 'Sensor data recorded',
                'data_id': sensor_data.id,
                'timestamp': sensor_data.timestamp
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def api_get_setpoint(request):
    """
    API endpoint for Raspberry Pi to get current temperature setpoint
    Query params: api_key
    """
    api_key = request.query_params.get('api_key', '')
    
    VALID_API_KEY = 'your_rpi_api_key_12345'
    if api_key != VALID_API_KEY:
        return Response({
            'error': 'Invalid API key'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    setpoint = TemperatureSetpoint.objects.filter(is_active=True).first()
    
    if setpoint:
        return Response({
            'setpoint_temperature': setpoint.setpoint_temperature,
            'updated_at': setpoint.updated_at
        })
    else:
        return Response({
            'setpoint_temperature': 25.0,
            'updated_at': None
        })


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def api_get_device_status(request):
    """
    API endpoint for Raspberry Pi to get device control status
    Query params: api_key
    """
    api_key = request.query_params.get('api_key', '')
    
    VALID_API_KEY = 'your_rpi_api_key_12345'
    if api_key != VALID_API_KEY:
        return Response({
            'error': 'Invalid API key'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    fan = DeviceControl.objects.filter(device='fan').first()
    heater = DeviceControl.objects.filter(device='heater').first()
    
    return Response({
        'fan': {
            'is_on': fan.is_on if fan else False,
            'last_updated': fan.last_updated if fan else None
        },
        'heater': {
            'is_on': heater.is_on if heater else False,
            'last_updated': heater.last_updated if heater else None
        }
    })


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def api_latest_sensor_data(request):
    """
    API endpoint to get latest sensor readings
    Query params: api_key
    """
    api_key = request.query_params.get('api_key', '')
    
    VALID_API_KEY = 'your_rpi_api_key_12345'
    if api_key != VALID_API_KEY:
        return Response({
            'error': 'Invalid API key'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    sensor_data = SensorData.objects.first()
    
    if sensor_data:
        return Response({
            'temperature': sensor_data.temperature,
            'humidity': sensor_data.humidity,
            'timestamp': sensor_data.timestamp
        })
    else:
        return Response({
            'error': 'No sensor data available'
        }, status=status.HTTP_404_NOT_FOUND)
