from django.contrib import admin

from users.models import User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'role'
    )
    list_display_links = ('username', 'email',)
    search_fields = ('username', 'email',)


admin.site.register(User, UserAdmin)