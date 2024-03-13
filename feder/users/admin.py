from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

from .models import User


class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class MyUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages["duplicate_username"])


class UserEmailVerifiedFilter(admin.SimpleListFilter):
    title = "email verified"
    parameter_name = "email_verified"

    def lookups(self, request, model_admin):
        return (
            ("yes", _("Yes")),
            ("no", _("No")),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(emailaddress__verified=True)
        if self.value() == "no":
            return queryset.filter(emailaddress__verified=False)


@admin.register(User)
class UserAdmin(AuthUserAdmin):
    form = MyUserChangeForm
    add_form = MyUserCreationForm
    fieldsets = list(AuthUserAdmin.fieldsets) + [
        (
            _("Content Editor"),
            {"fields": ("is_content_editor",)},
        ),
    ]
    actions = [
        "delete_never_logged_in",
    ]
    date_hierarchy = "date_joined"
    list_display = (
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "date_joined",
        "last_login",
    )
    list_filter = ("is_staff", "is_active", "is_superuser", UserEmailVerifiedFilter)
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("-id",)

    @admin.action(description=_("Delete selected users that never logged in"))
    def delete_never_logged_in(self, request, queryset):
        selected_never_logged_in = queryset.filter(last_login__isnull=True)
        count = selected_never_logged_in.count()
        for user_never_logged_in in selected_never_logged_in:
            object_repr = str(user_never_logged_in)
            self.log_deletion(request, user_never_logged_in, object_repr)
        selected_never_logged_in.delete()
        self.message_user(request, f"Deleted {count} users that never logged in.")

    def get_actions(self, request):
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions
