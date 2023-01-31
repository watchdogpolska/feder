import os

import sys


def environ(key, bool=False, required=True):
    if key not in os.environ:
        if required:
            sys.stderr.write(
                f"Set the environment variable {key} correctly. It's required!"
            )
            sys.exit(2)
        else:
            return None
    if bool:
        return os.environ[key].lower() == "true"
    return os.environ[key]
