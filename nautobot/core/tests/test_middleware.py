from copy import deepcopy
from unittest.mock import patch

from django.conf import settings
from django.test import override_settings
from django.urls import reverse
from django.utils import translation

from nautobot.core.settings_funcs import setup_structlog_logging
from nautobot.core.testing import TestCase

override_middleware = deepcopy(settings.MIDDLEWARE)
django_structlog_middleware = "django_structlog.middlewares.RequestMiddleware"
try:
    index_of_prometheus_after_middleware = override_middleware.index(
        "django_prometheus.middleware.PrometheusAfterMiddleware"
    )
    override_middleware.insert(index_of_prometheus_after_middleware, django_structlog_middleware)
except ValueError:
    override_middleware.append(django_structlog_middleware)


class MiddlewareTestCase(TestCase):
    @override_settings(
        _TESTING_STRUCTLOG=True,
        DEBUG=False,
        MIDDLEWARE=override_middleware,
        LOGGING=deepcopy(settings.LOGGING),
        INSTALLED_APPS=deepcopy(settings.INSTALLED_APPS),
    )
    def test_exception_handling_middleware(self):
        """Test that stack traces are also included for API view 500s.

        Note that a better test would probably be to assert the actual log output to be there, but this poses problems:
        - Colored output would need to be disabled or the ANSI codes stripped
        - The log message did not seem to output when I tried to reproduce this, I assume something about the way
          the structlog middleware is implemented is interfering
        """
        setup_structlog_logging(
            settings.LOGGING,
            settings.INSTALLED_APPS,
            settings.MIDDLEWARE,
        )
        with patch("nautobot.core.middleware.bind_extra_request_failed_metadata") as signal:
            result = self.client.get("/api/plugins/example-app/error/")
        # This assertion makes sure we actually got a HTTP 500 return code. This should be guaranteed, as the view
        # in question is incapable of doing anything else.
        self.assertEqual(result.status_code, 500)
        # This is the assertion that is actually testing our behaviour
        signal.send.assert_called()


class UserDefinedLanguageMiddlewareTestCase(TestCase):
    """Tests for `nautobot.core.middleware.UserDefinedLanguageMiddleware`."""

    def test_default_language_when_no_preference_set(self):
        """A user who never chose a language gets `LANGUAGE_CODE`."""
        response = self.client.get(reverse("home"))
        self.assertEqual(response.headers["Content-Language"], settings.LANGUAGE_CODE)

    def test_user_preference_is_activated(self):
        """A user's stored `language` preference is activated for their requests."""
        self.user.set_config("language", "de", commit=True)
        response = self.client.get(reverse("home"))
        self.assertEqual(response.headers["Content-Language"], "de")

    def test_unsupported_language_preference_is_ignored(self):
        """A stored preference not present in `LANGUAGES` falls back to the default language."""
        self.user.set_config("language", "de", commit=True)
        with override_settings(LANGUAGES=[("en", "English")]):
            response = self.client.get(reverse("home"))
        self.assertEqual(response.headers["Content-Language"], settings.LANGUAGE_CODE)

    def test_accept_language_header_is_not_honored(self):
        """Nautobot deliberately does not negotiate a language from `Accept-Language`."""
        response = self.client.get(reverse("home"), headers={"accept-language": "de,fr;q=0.9"})
        self.assertEqual(response.headers["Content-Language"], settings.LANGUAGE_CODE)

    def test_language_is_deactivated_after_response(self):
        """The activated language must not leak into the thread after the request completes."""
        self.user.set_config("language", "fr", commit=True)
        self.client.get(reverse("home"))
        self.assertEqual(translation.get_language(), settings.LANGUAGE_CODE)


class DocumentLanguageAttributesTestCase(TestCase):
    """The rendered `<html>` tag must declare the language actually in effect."""

    def test_default_language_attributes(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, f'<html lang="{settings.LANGUAGE_CODE}" dir="ltr"')

    def test_language_attributes_follow_user_preference(self):
        self.user.set_config("language", "zh-hans", commit=True)
        response = self.client.get(reverse("home"))
        self.assertContains(response, '<html lang="zh-hans" dir="ltr"')

    def test_admin_language_attributes_follow_user_preference(self):
        self.user.is_superuser = True
        self.user.is_staff = True
        self.user.save()
        self.user.set_config("language", "de", commit=True)
        response = self.client.get(reverse("admin:index"))
        self.assertContains(response, '<html lang="de" dir="ltr"')
