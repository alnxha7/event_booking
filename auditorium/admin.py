from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Auditorium


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
    list_display = ('user', 'location', 'capacity', 'price', 'approved')
    list_filter = ('approved',)
    actions = ['approve_auditoriums', 'reject_auditoriums']

    def approve_auditoriums(self, request, queryset):
        for auditorium in queryset:
            if auditorium.user:
                auditorium.approved = True
                auditorium.save()
        self.message_user(request, "Selected auditoriums have been approved.")
    approve_auditoriums.short_description = 'Approve selected auditoriums'

    def reject_auditoriums(self, request, queryset):
        for auditorium in queryset:
            if auditorium.user:
                auditorium.approved = False
                auditorium.save()
        self.message_user(request, "Selected auditoriums have been rejected.")
    reject_auditoriums.short_description = 'Reject selected auditoriums'


admin.site.register(User, UserAdmin)
admin.site.register(Auditorium, AuditoriumAdmin)