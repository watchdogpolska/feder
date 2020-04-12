from django.core.signing import TimestampSigner


class TokenSigner:
    signer = TimestampSigner()

    def unsign(self, value):
        return self.signer.unsign(value=value, max_age=60 * 60 * 24 * 7)

    def sign(self, value):
        return self.signer.sign(value)
