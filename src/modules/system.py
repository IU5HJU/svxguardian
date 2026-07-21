"""
System monitoring functions for SVX Guardian.
"""

import shutil


def get_disk_usage():
    """
    Restituisce le informazioni sull'utilizzo del disco.
    """

    total, used, free = shutil.disk_usage("/")

    percent = round((used / total) * 100, 1)

    return {
        "total": total,
        "used": used,
        "free": free,
        "percent": percent,
    }
