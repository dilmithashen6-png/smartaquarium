from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('public-dashboard/', views.public_dashboard, name='public_dashboard'),
    path('history/', views.data_history, name='data_history'),
    
    # Admin Control
    path('update-setpoint/', views.update_setpoint, name='update_setpoint'),
    path('control-device/', views.control_device, name='control_device'),
    
    # REST API for Raspberry Pi
    path('api/sensor-data/', views.api_sensor_data, name='api_sensor_data'),
    path('api/get-setpoint/', views.api_get_setpoint, name='api_get_setpoint'),
    path('api/get-device-status/', views.api_get_device_status, name='api_get_device_status'),
    path('api/latest-sensor/', views.api_latest_sensor_data, name='api_latest_sensor'),
]
