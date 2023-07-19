from django.contrib import admin
from escrow_app import models

class RoleAdmin(admin.ModelAdmin):
    list_display = (
        'Role_id',
        'Name',
    )
admin.site.register(models.Role, RoleAdmin)

class UserAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'email',
        'phone_number',
        'Role',
        'is_staff',
        'is_active',
    )
admin.site.register(models.User, UserAdmin)

class AppUserAdmin(admin.ModelAdmin):
    list_display = (
        'app_user',
        'email',
        'reference_id',
        'is_verified',
        'is_updated',
        'is_staff',
        'is_active',
    )
admin.site.register(models.AppUsers, AppUserAdmin)