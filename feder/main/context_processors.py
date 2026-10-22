from allauth.account.adapter import get_adapter


def signup(request):
    return {"signup_open": get_adapter(request).is_open_for_signup(request)}
