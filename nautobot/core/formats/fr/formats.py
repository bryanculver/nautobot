"""
Format overrides for the `fr` locale.

Forwards only the date/time format settings that the operator explicitly configured; everything else
falls through to `django.conf.locale.fr.formats`. See `nautobot.core.formats` for the rationale.
"""

from nautobot.core.formats import operator_format_overrides as __getattr__  # noqa: F401
