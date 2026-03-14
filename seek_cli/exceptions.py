class SeekCliError(Exception):
    """Base exception for seek-cli."""


class NotImplementedYetError(SeekCliError):
    """Raised for features whose interface is ready before live integration."""


class TransportError(SeekCliError):
    """Raised when SEEK transport cannot fetch or parse data."""
