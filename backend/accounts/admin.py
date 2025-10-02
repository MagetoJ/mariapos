from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, UserSession, WorkShift

@admin.register(WorkShift)
class WorkShiftAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_time', 'end_time', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'start_time', 'end_time', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'name', 'role', 'is_active', 'is_staff', 'room_number', 'created_at')
    list_filter = ('role', 'is_active', 'is_staff', 'created_at', 'assigned_shift')
    search_fields = ('email', 'name', 'phone', 'room_number')
    readonly_fields = ('id', 'created_at', 'updated_at', 'last_login')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Authentication', {
            'fields': ('id', 'email', 'password')
        }),
        ('Personal Information', {
            'fields': ('name', 'phone', 'role')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Guest Information', {
            'fields': ('room_number', 'table_number', 'check_in_date', 'check_out_date'),
            'classes': ('collapse',)
        }),
        ('Work Assignment', {
            'fields': ('assigned_shift',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_login'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        ('Create User', {
            'classes': ('wide',),
            'fields': ('email', 'name', 'role', 'password1', 'password2', 'is_active')
        }),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Show guest fields only for guest users
        if obj and obj.role != 'guest':
            if 'room_number' in form.base_fields:
                form.base_fields['room_number'].widget.attrs['style'] = 'display:none;'
            if 'table_number' in form.base_fields:
                form.base_fields['table_number'].widget.attrs['style'] = 'display:none;'
        return form

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'shift', 'login_time', 'logout_time', 'duration_display', 'orders_handled', 'revenue_generated', 'is_active')
    list_filter = ('is_active', 'shift', 'login_time')
    search_fields = ('user__name', 'user__email', 'shift__name')
    readonly_fields = ('id', 'duration_display', 'created_at', 'updated_at')
    date_hierarchy = 'login_time'
    
    fieldsets = (
        ('Session Information', {
            'fields': ('id', 'user', 'shift', 'is_active')
        }),
        ('Timing', {
            'fields': ('login_time', 'logout_time', 'duration_display')
        }),
        ('Performance Metrics', {
            'fields': ('orders_handled', 'revenue_generated')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def duration_display(self, obj):
        duration = obj.duration
        if duration:
            hours, remainder = divmod(duration.total_seconds(), 3600)
            minutes, _ = divmod(remainder, 60)
            return f"{int(hours)}h {int(minutes)}m"
        return "Ongoing" if obj.is_active else "N/A"
    duration_display.short_description = 'Duration'
