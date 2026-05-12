from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.db.models.query import QuerySet
from django.http import HttpRequest

from .models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    extra = 0
    can_delete = False
    verbose_name = "Профиль"
    verbose_name_plural = "Профили"


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "nickname")
    search_fields = ("nickname", "user__username", "user__email")
    list_filter = ("user__is_active",)
    raw_id_fields = ("user",)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")
    

class CustomUserAdmin(UserAdmin):
    inlines = (*UserAdmin.inlines, ProfileInline)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
    