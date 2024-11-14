from django.contrib import admin
from .models import User, Preferences, Goals, Subtasks, Dashboard
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _


class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'profile_image')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name'),
        }),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions')


class PreferencesAdmin(admin.ModelAdmin):
    list_display = ('user', 'roles', 'time_of_day', 'sound')
    search_fields = ('user__email', 'roles')


class GoalsAdmin(admin.ModelAdmin):
    list_display = ('user', 'description', 'completed', 'due_date')
    search_fields = ('user__email', 'description')
    list_filter = ('completed', 'due_date')


class SubtasksAdmin(admin.ModelAdmin):
    list_display = ('tasks', 'description', 'completed')
    search_fields = ('tasks__description', 'description')
    list_filter = ('completed',)


class DashboardAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_total_goals', 'get_total_subtasks', 'get_completed_percentage')
    search_fields = ('user__email',)

    def get_total_goals(self, obj):
        return obj.goals.count()

    def get_total_subtasks(self, obj):
        return obj.subtasks.count()

    def get_completed_percentage(self, obj):
        return obj.calculate_completed_percentage()
    
    

    get_total_goals.short_description = 'Total Goals'
    get_total_subtasks.short_description = 'Total Subtasks'
    get_completed_percentage.short_description = 'Completed Percentage'
    
    
    
    
from .models import BlockedSite

@admin.register(BlockedSite)
class BlockedSiteAdmin(admin.ModelAdmin):
    list_display = ('user', 'url')
    search_fields = ('user__username', 'url')


admin.site.register(User, UserAdmin)
admin.site.register(Preferences, PreferencesAdmin)
admin.site.register(Goals, GoalsAdmin)
admin.site.register(Subtasks, SubtasksAdmin)
admin.site.register(Dashboard, DashboardAdmin)
