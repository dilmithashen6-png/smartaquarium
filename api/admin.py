from django.contrib import admin
from .models import SensorData, DeviceControl, TemperatureSetpoint

@admin.register(SensorData)
class SensorDataAdmin(admin.ModelAdmin):
    list_display = ('temperature', 'humidity', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('temperature', 'humidity')
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)
    
    def has_add_permission(self, request):
        # Prevent manual addition, only allow API submissions
        return False


@admin.register(DeviceControl)
class DeviceControlAdmin(admin.ModelAdmin):
    list_display = ('device', 'is_on', 'last_updated')
    list_editable = ('is_on',)
    list_filter = ('device', 'is_on', 'last_updated')
    readonly_fields = ('device', 'last_updated')
    
    fieldsets = (
        ('Device Information', {
            'fields': ('device',)
        }),
        ('Control Status', {
            'fields': ('is_on', 'last_updated')
        }),
    )


@admin.register(TemperatureSetpoint)
class TemperatureSetpointAdmin(admin.ModelAdmin):
    list_display = ('setpoint_temperature', 'is_active', 'created_by', 'updated_at')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('setpoint_temperature',)
    readonly_fields = ('created_by', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Setpoint Configuration', {
            'fields': ('setpoint_temperature', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
