"""Refoss exceptions."""
from __future__ import annotations


class RefossError(Exception):
    """Base class for refoss_ha errors."""


class RefossSocketInitErr(RefossError):
    """Exception raised when socket init fail."""
