class FederError(Exception):
    """
    General Feder exception.
    """

    pass


class FederConfigError(FederError):
    """
    Exception related to invalid configuration.
    """

    pass


class FederValueError(FederError):
    """
    Exception occurring when improper value has been encountered.
    """

    pass
