from django.contrib import admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from .models import User, Profile
from django.contrib.auth.forms import PasswordChangeForm


# Register your models here.
class ProfileAdmin(admin.TabularInline):
    model = Profile


class UserAdminInterface(BaseUserAdmin):
    change_password_form = PasswordChangeForm
    list_display = ('username', 'id', 'name', 'email', 'gender',)
    list_filter = ('admin',)
    fieldsets = (
        (None, {'fields': ('username', 'email',)}),
        ('Personal info', {'fields': ('name', 'gender',)}),
        ('Permissions', {'fields': ('admin', 'staff')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'gender', 'name', 'password1', 'password2',)}
         ),
    )
    inlines = [ProfileAdmin]
    search_fields = ('username',)
    ordering = ('id',)

    def get_queryset(self, request):
        return self.model.objects.filter(admin=False, staff=False)


admin.site.register(User, UserAdminInterface)


class __Admin__(admin.ModelAdmin):
    list_display = ('username', 'email', 'admin', 'staff')
    fieldsets = (
        (None, {'fields': ('username', 'email',)}),
        ('Personal info', {'fields': ('name', 'gender',)}),
        ('Permissions', {'fields': ('admin', 'staff', 'user_permissions', 'groups')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'gender', 'name', 'password1', 'password2',)}
         ),
    )
    filter_horizontal = ('user_permissions',)


class Administrator(User):
    class Meta:
        proxy = True


class Admin(__Admin__):
    def get_queryset(self, request):
        return self.model.objects.filter(admin=True, staff=True)


admin.site.register(Administrator, Admin)
