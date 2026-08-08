"""
Locale-aware resolution of Nautobot's date/time format settings.

Nautobot lets an operator pin date/time rendering globally via `DATE_FORMAT`, `DATETIME_FORMAT`,
`SHORT_DATE_FORMAT`, `SHORT_DATETIME_FORMAT`, and `TIME_FORMAT`. Django, meanwhile, wants to render
dates the way each active locale does. `FORMAT_MODULE_PATH` points here so that Nautobot can
arbitrate between the two, with this precedence:

1. A format the operator explicitly configured wins, in *every* locale. Organizations that mandate
   ISO dates did so on purpose, and silently ignoring that for non-English users is a bug.
2. Otherwise, non-English locales use Django's own per-locale defaults
   (`django.conf.locale.<locale>.formats`).
3. English keeps Nautobot's opinionated defaults, which is what `en/formats.py` forwards
   unconditionally.

"Explicitly configured" is detected by comparing the live setting against `NAUTOBOT_FORMAT_DEFAULTS`
below. Nautobot's config file star-imports the core settings, so there is no way to tell at load time
whether a value was assigned by the operator or merely inherited; a value differing from the shipped
default is the faithful proxy. It also behaves identically whether the value arrived from an
environment variable, `nautobot_config.py`, or `override_settings` in a test.

The one accepted imprecision: an operator who explicitly sets a format to exactly the Nautobot
default is indistinguishable from one who left it alone, and so gets locale defaults in non-English
locales. This is documented in `settings.yaml`.
"""

# Nautobot's own defaults for the five format settings, and the single source of truth for them --
# `nautobot.core.settings` imports these rather than repeating the literals.
#
# This module is imported by `settings.py` *before* Django is configured, so it must not touch
# `django.conf.settings` at import time.
NAUTOBOT_FORMAT_DEFAULTS = {
    "DATE_FORMAT": "N j, Y",
    "DATETIME_FORMAT": "N j, Y g:i a",
    "SHORT_DATE_FORMAT": "Y-m-d",
    "SHORT_DATETIME_FORMAT": "Y-m-d H:i",
    "TIME_FORMAT": "g:i a",
}


def operator_format_overrides(name):
    """
    PEP 562 module `__getattr__` shared by every non-English locale format stub.

    Forwards a format setting only when the operator explicitly configured a non-default value.
    Otherwise raises `AttributeError`, which makes Django's `iter_format_modules()` fall through to
    `django.conf.locale.<locale>.formats` and use that locale's own conventions.

    Deliberately does *not* forward input formats (`DATE_INPUT_FORMATS` and friends) or the
    separator settings for non-English locales -- parsing and grouping in the locale's own style is
    the point of switching locale in the first place.
    """
    default = NAUTOBOT_FORMAT_DEFAULTS.get(name)
    if default is not None:
        from django.conf import settings  # Imported lazily; see the module docstring.

        value = getattr(settings, name)
        if value != default:
            return value
    raise AttributeError(name)
