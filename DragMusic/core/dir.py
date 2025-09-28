import os

from ..logging import LOGGER


def dirr():
    if not os.path.isdir("/tmp/downloads"):
        os.makedirs("/tmp/downloads")
    if not os.path.isdir("/tmp/cache"):
        os.makedirs("/tmp/cache")
    
    for file in os.listdir("/tmp/downloads"):
        if file.endswith((".jpg", ".jpeg", ".png")):
            os.remove(os.path.join("/tmp/downloads", file))

    LOGGER(__name__).info("Directories Updated.")
