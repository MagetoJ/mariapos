from django.contrib import admin
from django.utils.html import format_html
from .models import Guest, GuestPreference, RoomServiceRequest

@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'room_number', 'check_in_date', 'check_out_date', 'status', 'total_spent', 'created_at')
    list_filter = ('status', 'check_in_date', 'check_out_date', 'created_at')
    search_fields = ('name', 'email', 'phone', 'room_number', 'passport_number')
    readonly_fields = ('id', 'total_spent', 'created_at', 'updated_at')
    date_hierarchy = 'check_in_date'
    
    fieldsets = (
        ('Guest Information', {
            'fields': ('id', 'name', 'email', 'phone', 'date_of_birth')
        }),
        ('Stay Details', {
            'fields': ('room_number', 'check_in_date', 'check_out_date', 'status')
        }),
        ('Identification', {
            'fields': ('passport_number', 'id_number', 'nationality'),
            'classes': ('collapse',)
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone'),
            'classes': ('collapse',)
        }),
        ('Special Requirements', {
            'fields': ('special_requests', 'dietary_restrictions', 'accessibility_needs'),
            'classes': ('collapse',)
        }),
        ('Financial', {
            'fields': ('total_spent',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(GuestPreference)
class GuestPreferenceAdmin(admin.ModelAdmin):
    list_display = ('guest', 'preference_type', 'preference_value', 'created_at')
    list_filter = ('preference_type', 'created_at')
    search_fields = ('guest__name', 'preference_value')
    readonly_fields = ('id', 'created_at')

@admin.register(RoomServiceRequest)
class RoomServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('guest', 'request_type', 'status', 'priority', 'requested_at', 'completed_at')
    list_filter = ('request_type', 'status', 'priority', 'requested_at')
    search_fields = ('guest__name', 'guest__room_number', 'description')
    readonly_fields = ('id', 'requested_at', 'completed_at')
    date_hierarchy = 'requested_at'
