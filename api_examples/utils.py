import os

import sys


def environ(key, bool=False, required=True):
    if key not in os.environ:
        if required:
            sys.stderr.write(
                "Set the environment variable {} correctly. It's required!".format(key)
            )
            sys.exit(2)
        else:
            return None
    if bool:
        return os.environ[key].lower() == "true"
    return os.environ[key]
