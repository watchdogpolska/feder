from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings


# This adapter controls the signup functionality. By default, signup is
# disabled and users can only sign in if they already have an account -
# new users are manually added by admins. Signup can be enabled with
# the ACCOUNT_ALLOW_SIGNUP setting (DJANGO_ACCOUNT_ALLOW_SIGNUP env variable).
class NoSignupAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return getattr(settings, "ACCOUNT_ALLOW_SIGNUP", False)
