"""Mailman3 Commander package."""

__version__ = "0.1.1"

from .docker_mailman import add_members, list_lists, list_members

__all__ = [
    "__version__",
    "add_members",
    "list_lists",
    "list_members",
]
