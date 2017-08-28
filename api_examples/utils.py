import os

import sys


def environ(key, bool=False):
    if key not in os.environ:
        sys.stderr.write("Set the environemnt variable {} correctly. It's required!".format(key))
        sys.exit(2)
    if bool:
        return os.environ[key].lower() == 'true'
    return os.environ[key]
