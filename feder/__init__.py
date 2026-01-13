# PEP 396: The __version__ attribute's value SHOULD be a string.
__version__ = "1.5.61.deps"


# Compatibility to eg. django-rest-framework
VERSION = tuple(
    int(num) if num.isdigit() else num
    for num in __version__.replace("-", ".", 1).split(".")
)


def get_version():
    return __version__
