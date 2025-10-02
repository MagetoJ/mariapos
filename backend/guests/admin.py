from django.contrib import admin
from django.utils.html import format_html
from .models import Guest, GuestPreference, GuestGroup, GuestFeedback

@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ('full_name_display', 'email', 'room_number', 'checkin_date', 'checkout_date', 'status', 'guest_type', 'is_vip', 'created_at')
    list_filter = ('status', 'guest_type', 'is_vip', 'expected_checkin', 'expected_checkout', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'room_number', 'guest_number')
    readonly_fields = ('id', 'guest_number', 'stay_duration', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    date_hierarchy = 'expected_checkin'
    
    fieldsets = (
        ('Guest Information', {
            'fields': (
                'id', 'guest_number', 'first_name', 'last_name', 'email', 'phone'
            )
        }),
        ('Address', {
            'fields': (
                'address', 'city', 'country', 'postal_code'
            ),
            'classes': ('collapse',)
        }),
        ('Identification', {
            'fields': (
                'id_type', 'id_number'
            ),
            'classes': ('collapse',)
        }),
        ('Stay Details', {
            'fields': (
                'room_number', 'status', 'guest_type', 'expected_checkin', 'actual_checkin',
                'expected_checkout', 'actual_checkout', 'stay_duration'
            )
        }),
        ('Preferences & Requests', {
            'fields': (
                'dietary_preferences', 'special_requests', 'preferred_language',
                'housekeeping_preferences', 'minibar_access'
            ),
            'classes': ('collapse',)
        }),
        ('Emergency Contact', {
            'fields': (
                'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship'
            ),
            'classes': ('collapse',)
        }),
        ('VIP & Loyalty', {
            'fields': (
                'is_vip', 'loyalty_number', 'previous_stays', 'company'
            ),
            'classes': ('collapse',)
        }),
        ('Staff & Notes', {
            'fields': (
                'assigned_staff', 'notes'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['mark_checked_in', 'mark_checked_out', 'mark_vip', 'send_welcome_message']
    
    def full_name_display(self, obj):
        return obj.full_name
    full_name_display.short_description = 'Guest Name'
    
    def checkin_date(self, obj):
        if obj.actual_checkin:
            return format_html('<span style="color: green;">✓ {}</span>', obj.actual_checkin.strftime('%Y-%m-%d %H:%M'))
        return format_html('<span style="color: orange;">Expected: {}</span>', obj.expected_checkin.strftime('%Y-%m-%d %H:%M'))
    checkin_date.short_description = 'Check-in Date'
    
    def checkout_date(self, obj):
        if obj.actual_checkout:
            return format_html('<span style="color: red;">✓ {}</span>', obj.actual_checkout.strftime('%Y-%m-%d %H:%M'))
        return format_html('<span style="color: blue;">Expected: {}</span>', obj.expected_checkout.strftime('%Y-%m-%d %H:%M'))
    checkout_date.short_description = 'Check-out Date'
    
    def mark_checked_in(self, request, queryset):
        count = 0
        for guest in queryset:
            if guest.status != 'checked_in':
                guest.check_in()
                count += 1
        self.message_user(request, f'{count} guests checked in successfully.')
    mark_checked_in.short_description = 'Check in selected guests'
    
    def mark_checked_out(self, request, queryset):
        count = 0
        for guest in queryset:
            if guest.status == 'checked_in':
                guest.check_out()
                count += 1
        self.message_user(request, f'{count} guests checked out successfully.')
    mark_checked_out.short_description = 'Check out selected guests'
    
    def mark_vip(self, request, queryset):
        updated = queryset.update(is_vip=True)
        self.message_user(request, f'{updated} guests marked as VIP.')
    mark_vip.short_description = 'Mark selected guests as VIP'
    
    def send_welcome_message(self, request, queryset):
        count = queryset.count()
        self.message_user(request, f'Welcome message sent to {count} guests.')
    send_welcome_message.short_description = 'Send welcome message to selected guests'


@admin.register(GuestPreference)
class GuestPreferenceAdmin(admin.ModelAdmin):
    list_display = ('guest_name', 'category', 'preference_key', 'preference_value', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('guest__first_name', 'guest__last_name', 'preference_key', 'preference_value')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Preference Information', {
            'fields': ('guest', 'category', 'preference_key', 'preference_value', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def guest_name(self, obj):
        return obj.guest.full_name
    guest_name.short_description = 'Guest'


@admin.register(GuestGroup)
class GuestGroupAdmin(admin.ModelAdmin):
    list_display = ('group_name', 'group_leader', 'total_guests', 'group_type', 'group_rate_applied', 'created_at')
    list_filter = ('group_type', 'group_rate_applied', 'created_at')
    search_fields = ('group_name', 'group_leader__first_name', 'group_leader__last_name')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Group Information', {
            'fields': ('group_name', 'group_leader', 'total_guests', 'group_type')
        }),
        ('Pricing & Arrangements', {
            'fields': ('group_rate_applied', 'group_discount_percent', 'special_arrangements')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(GuestFeedback)
class GuestFeedbackAdmin(admin.ModelAdmin):
    list_display = ('guest_name', 'category', 'rating_display', 'is_public', 'has_response', 'created_at')
    list_filter = ('category', 'rating', 'is_public', 'is_anonymous', 'created_at')
    search_fields = ('guest__first_name', 'guest__last_name', 'comments', 'management_response')
    readonly_fields = ('id', 'created_at')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Feedback Information', {
            'fields': ('guest', 'category', 'rating', 'comments', 'is_anonymous', 'is_public')
        }),
        ('Management Response', {
            'fields': ('management_response', 'responded_by', 'responded_at')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    actions = ['mark_public', 'mark_private', 'require_response']
    
    def guest_name(self, obj):
        if obj.is_anonymous:
            return "Anonymous Guest"
        return obj.guest.full_name
    guest_name.short_description = 'Guest'
    
    def rating_display(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        color = ['red', 'orange', 'yellow', 'lightgreen', 'green'][obj.rating - 1]
        return format_html('<span style="color: {};">{} ({})</span>', color, stars, obj.rating)
    rating_display.short_description = 'Rating'
    
    def has_response(self, obj):
        if obj.management_response:
            return format_html('<span style="color: green;">✓ Responded</span>')
        return format_html('<span style="color: red;">✗ No Response</span>')
    has_response.short_description = 'Response Status'
    
    def mark_public(self, request, queryset):
        updated = queryset.update(is_public=True)
        self.message_user(request, f'{updated} feedback items marked as public.')
    mark_public.short_description = 'Mark feedback as public'
    
    def mark_private(self, request, queryset):
        updated = queryset.update(is_public=False)
        self.message_user(request, f'{updated} feedback items marked as private.')
    mark_private.short_description = 'Mark feedback as private'
    
    def require_response(self, request, queryset):
        count = queryset.filter(management_response__exact='').count()
        self.message_user(request, f'{count} feedback items require management response.')
    require_response.short_description = 'Identify items needing response'