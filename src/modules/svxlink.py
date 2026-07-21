"""
Modulo per il controllo del servizio SvxLink.
"""

import subprocess


def get_service_status(service_name="svxlink"):
    """
    Restituisce True se il servizio è attivo,
    False in caso contrario.
    """

    result = subprocess.run(
        ["systemctl", "is-active", service_name],
        capture_output=True,
        text=True
    )

    return result.stdout.strip() == "active"
