from allauth.account.adapter import DefaultAccountAdapter


# This adapter is used to disable the signup functionality
# and only allow users to sign in if they already have an account
# Until more robust signup process is agreed new users will be manually
# added by admins
class NoSignupAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return False
