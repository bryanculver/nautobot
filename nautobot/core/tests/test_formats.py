import datetime
from importlib import import_module

from django.conf import settings
from django.template.defaultfilters import date, time
from django.test import override_settings
from django.utils import translation
from django.utils.translation import to_locale

from nautobot.core.formats import NAUTOBOT_FORMAT_DEFAULTS, operator_format_overrides
from nautobot.core.testing import TestCase

# A date/time with an unambiguous day-vs-month reading, so a wrongly-applied format is visible.
SAMPLE_DATE = datetime.date.fromisoformat("2026-02-23")
SAMPLE_DATETIME = datetime.datetime.fromisoformat("2026-02-23 16:54:03")

# Non-English languages that Nautobot ships format stubs for.
NON_ENGLISH_LANGUAGES = [code for code, _ in settings.LANGUAGES if code != "en"]


class FormatsTestCase(TestCase):
    def test_settings_overrides_propagate_to_formats(self):
        with self.subTest("implicit DATE_FORMAT"), override_settings(DATE_FORMAT="Y/m/d"):
            self.assertEqual(date(datetime.date.fromisoformat("2026-02-23")), "2026/02/23")

        with self.subTest("explicit DATE_FORMAT"), override_settings(DATE_FORMAT="Y/m/d"):
            self.assertEqual(date(datetime.date.fromisoformat("2026-02-23"), "DATE_FORMAT"), "2026/02/23")

        with self.subTest("DATETIME_FORMAT"), override_settings(DATETIME_FORMAT="Y/m/d H-i-s"):
            self.assertEqual(
                date(datetime.datetime.fromisoformat("2026-02-23 16:54:03"), "DATETIME_FORMAT"), "2026/02/23 16-54-03"
            )

        with self.subTest("SHORT_DATE_FORMAT"), override_settings(SHORT_DATE_FORMAT="m/d"):
            self.assertEqual(date(datetime.date.fromisoformat("2026-02-23"), "SHORT_DATE_FORMAT"), "02/23")

        with self.subTest("SHORT_DATETIME_FORMAT"), override_settings(SHORT_DATETIME_FORMAT="m/d H-i"):
            self.assertEqual(
                date(datetime.datetime.fromisoformat("2026-02-23 16:54:03"), "SHORT_DATETIME_FORMAT"), "02/23 16-54"
            )

        with self.subTest("TIME_FORMAT"), override_settings(TIME_FORMAT="H/i.s"):
            self.assertEqual(time(datetime.datetime.fromisoformat("2026-02-23 16:54:03"), "TIME_FORMAT"), "16/54.03")


class LocaleFormatsTestCase(TestCase):
    """
    Tests for the D-1 precedence rule implemented in `nautobot.core.formats`:

    an explicitly-configured operator format wins in every language; otherwise each non-English
    language uses Django's own conventions for that language.
    """

    def test_settings_defaults_match_canonical_defaults(self):
        """`settings.py` must derive its format defaults from `NAUTOBOT_FORMAT_DEFAULTS`."""
        for name, expected in NAUTOBOT_FORMAT_DEFAULTS.items():
            with self.subTest(name):
                self.assertEqual(getattr(settings, name), expected)

    def test_every_shipped_language_has_a_format_stub(self):
        """
        Adding a language to `LANGUAGES` must come with a format stub, or operator-configured
        formats would be silently ignored for that language.
        """
        for language in NON_ENGLISH_LANGUAGES:
            with self.subTest(language):
                module = import_module(f"{settings.FORMAT_MODULE_PATH}.{to_locale(language)}.formats")
                self.assertIs(module.__getattr__, operator_format_overrides)

    def test_unset_formats_fall_through_to_django_locale_defaults(self):
        """
        With no operator override, each language renders dates its own way.

        Compared against Django's own format modules rather than hardcoded strings, so that a
        Django upgrade adjusting a locale's conventions does not fail this test spuriously.
        """
        for language in NON_ENGLISH_LANGUAGES:
            django_formats = import_module(f"django.conf.locale.{to_locale(language)}.formats")
            for name in NAUTOBOT_FORMAT_DEFAULTS:
                expected_format = getattr(django_formats, name, None)
                if expected_format is None:
                    # Django does not override this format for this locale; it inherits our setting.
                    continue
                # Both renders happen under the language, so month/day *names* are localized too and
                # only the format string itself is under test.
                with self.subTest(language=language, format=name), translation.override(language):
                    self.assertEqual(date(SAMPLE_DATETIME, name), date(SAMPLE_DATETIME, expected_format))

    def test_locale_defaults_actually_differ_from_english(self):
        """
        Guard against the whole mechanism silently no-op'ing.

        If this fails, every language is rendering English formats and the fall-through above is
        vacuously true.
        """
        english = date(SAMPLE_DATE, "DATE_FORMAT")
        for language in NON_ENGLISH_LANGUAGES:
            with self.subTest(language), translation.override(language):
                self.assertNotEqual(date(SAMPLE_DATE, "DATE_FORMAT"), english)

    def test_explicit_operator_format_wins_in_every_language(self):
        """The D-1 rule: a deliberately-configured format is not silently dropped for non-English users."""
        with override_settings(DATE_FORMAT="Y/m/d"):
            for language in ["en", *NON_ENGLISH_LANGUAGES]:
                with self.subTest(language), translation.override(language):
                    self.assertEqual(date(SAMPLE_DATE, "DATE_FORMAT"), "2026/02/23")

    def test_explicit_operator_format_wins_for_every_format_setting(self):
        overrides = {
            "DATE_FORMAT": ("Y/m/d", date, SAMPLE_DATE, "2026/02/23"),
            "DATETIME_FORMAT": ("Y/m/d H-i-s", date, SAMPLE_DATETIME, "2026/02/23 16-54-03"),
            "SHORT_DATE_FORMAT": ("m/d", date, SAMPLE_DATE, "02/23"),
            "SHORT_DATETIME_FORMAT": ("m/d H-i", date, SAMPLE_DATETIME, "02/23 16-54"),
            "TIME_FORMAT": ("H/i.s", time, SAMPLE_DATETIME, "16/54.03"),
        }
        for name, (format_string, renderer, value, expected) in overrides.items():
            with override_settings(**{name: format_string}):
                for language in NON_ENGLISH_LANGUAGES:
                    with self.subTest(format=name, language=language), translation.override(language):
                        self.assertEqual(renderer(value, name), expected)

    def test_partial_override_leaves_other_formats_localized(self):
        """Setting one format must not drag the others away from their locale defaults."""
        for language in NON_ENGLISH_LANGUAGES:
            django_formats = import_module(f"django.conf.locale.{to_locale(language)}.formats")
            expected_time_format = getattr(django_formats, "TIME_FORMAT", None)
            if expected_time_format is None:
                continue
            with self.subTest(language), override_settings(DATE_FORMAT="Y/m/d"), translation.override(language):
                self.assertEqual(date(SAMPLE_DATE, "DATE_FORMAT"), "2026/02/23")
                self.assertEqual(time(SAMPLE_DATETIME, "TIME_FORMAT"), time(SAMPLE_DATETIME, expected_time_format))

    def test_english_keeps_nautobot_defaults(self):
        """English is Nautobot's opinionated default experience, not Django's `en` locale."""
        with translation.override("en"):
            self.assertEqual(
                date(SAMPLE_DATE, "DATE_FORMAT"), date(SAMPLE_DATE, NAUTOBOT_FORMAT_DEFAULTS["DATE_FORMAT"])
            )

    def test_operator_format_overrides_raises_for_unknown_and_default_values(self):
        """Unit-level check of the fall-through contract that the stubs depend on."""
        with self.subTest("unknown setting"):
            with self.assertRaises(AttributeError):
                operator_format_overrides("DATE_INPUT_FORMATS")

        with self.subTest("value left at the Nautobot default"):
            with self.assertRaises(AttributeError):
                operator_format_overrides("DATE_FORMAT")

        with self.subTest("value explicitly configured"), override_settings(DATE_FORMAT="Y/m/d"):
            self.assertEqual(operator_format_overrides("DATE_FORMAT"), "Y/m/d")
