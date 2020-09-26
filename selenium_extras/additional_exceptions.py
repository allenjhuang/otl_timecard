class Error(Exception):
    """Base class for exceptions within this module."""
    pass


class BrowserNotExpected(Error):
    """Raised when an unexpected browser string is passed."""
    pass


class IncorrectLoginDetails(Error):
    """Raised when failed to pass Oracle Single Sign On."""
    pass


class MaxTriesReached(Error):
    """Raised when max tries have been reached for an action."""
    pass


class SubtaskNotFound(Error):
    """Raised when a line item's subtask is not found."""
    pass