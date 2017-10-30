from django.contrib import admin
from .models import LocationSearch, Profile
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin


class LocationSearchAdmin(admin.ModelAdmin):
    list_display = ('food', 'location', 'searched_by', 'search_date')
    list_filter = ('updated',)
    search_fields = ('food', 'location')


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, )
    list_display = ('username', 'email', 'get_date_of_birth', 'get_avatar', 'is_active', 'is_staff')
    list_select_related = ('profile',)
    search_fields = ('username', )

    def get_date_of_birth(self, instance):
        return instance.profile.date_of_birth
    get_date_of_birth.short_description = 'Birthday'

    def get_avatar(self, instance):
        return instance.profile.avatar

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(LocationSearch, LocationSearchAdmin)
