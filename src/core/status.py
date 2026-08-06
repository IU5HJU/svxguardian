"""
SVX Guardian shared status enumerations.

Defines the operational states used across monitors, APIs,
console output and dashboard components.
"""

from enum import Enum


class StringEnum(str, Enum):
    """
    Base enumeration whose members also behave as strings.
    """

    def __str__(self) -> str:
        """
        Return the serialized value of the enumeration member.
        """

        return self.value


class ServiceStatus(StringEnum):
    """
    Generic service operating status.
    """

    UNKNOWN = "UNKNOWN"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"
    ERROR = "ERROR"


class EchoLinkStatus(StringEnum):
    """
    EchoLink directory registration status.
    """

    UNKNOWN = "UNKNOWN"
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    DNS_ERROR = "DNS_ERROR"
    ERROR = "ERROR"


class ReflectorStatus(StringEnum):
    """
    SvxReflector connection status.
    """

    UNKNOWN = "UNKNOWN"
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"
    RECONNECTING = "RECONNECTING"
    DISCONNECTED = "DISCONNECTED"
    AUTH_ERROR = "AUTH_ERROR"
    TIMEOUT = "TIMEOUT"
    ERROR = "ERROR"


class HealthStatus(StringEnum):
    """
    Overall node health status.
    """

    UNKNOWN = "UNKNOWN"
    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
