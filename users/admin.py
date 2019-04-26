import logging

from django.contrib import admin

from .models import AppUser

_LOGGER = logging.getLogger(__name__)


class AppUserAdmin(admin.ModelAdmin):
    readonly_fields = ('email', 'is_active',)
    list_display = ('email', 'is_superuser', 'is_active',)

    search_fields = ('email',)

    fieldsets = (
        (None, {
            'fields': ('email', 'is_active', ),
        }),
    )

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        # we pass 'update_fields' so that the signal receiver knows
        # the 'is_active' field has been updated, which would then
        # result in an email been sent to the user.
        # Note that since we are only passing 'update_fields' here,
        # activating the user's account from anywhere else other than
        # the django admin page would result in no email being sent
        # to the user.
        # status is included so it will be synchronized
        obj.save(update_fields=['is_active', ])

    def get_actions(self, request):
        """ Remove actions bar.
        """
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


admin.site.register(AppUser, AppUserAdmin)
