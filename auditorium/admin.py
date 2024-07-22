from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Auditorium, BookingHistory

class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Personal info', {'fields': ('role',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active', 'is_superuser')
    search_fields = ('email', 'username')
    ordering = ('email',)

class AuditoriumAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'get_email', 'location', 'capacity', 'price', 'approved')
    actions = ['approve_auditoriums', 'reject_auditoriums']

    def get_username(self, obj):
        return obj.user.username

    def get_email(self, obj):
        return obj.user.email

    get_username.short_description = 'Username'
    get_email.short_description = 'Email'

    def approve_auditoriums(self, request, queryset):
        queryset.update(approved=True)
        self.message_user(request, "Selected auditoriums have been approved.")

    approve_auditoriums.short_description = 'Approve selected auditoriums'

    def reject_auditoriums(self, request, queryset):
        queryset.update(approved=False)
        self.message_user(request, "Selected auditoriums have been rejected.")

    reject_auditoriums.short_description = 'Reject selected auditoriums'

class BookingHistoryAdmin(admin.ModelAdmin):
    list_display = ('get_auditorium_name', 'user', 'date_booked', 'card_number', 'final_price', 'admin_amount')
    search_fields = ('auditorium__user__username', 'user__email', 'card_number')

    def get_auditorium_name(self, obj):
        return obj.auditorium.user.username

    get_auditorium_name.short_description = 'Auditorium Name'

admin.site.register(User, UserAdmin)
admin.site.register(Auditorium, AuditoriumAdmin)
admin.site.register(BookingHistory, BookingHistoryAdmin)
