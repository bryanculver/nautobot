"""
Unit tests for titles.py following Nautobot testing conventions.
"""

import re

from django.template import Context
from django.utils import translation

from nautobot.core.testing import TestCase
from nautobot.core.ui.titles import DEFAULT_TITLES, Titles, TRANSLATABLE_TITLE_MESSAGES
from nautobot.dcim.models import LocationType


class TitlesTestCase(TestCase):
    """Test cases for the base Titles class."""

    def setUp(self):
        self.titles = Titles()

    def test_init_with_defaults(self):
        """Test that Titles initializes with default titles."""
        self.assertEqual(self.titles.titles, DEFAULT_TITLES)
        self.assertEqual(self.titles.template_plugins, ["helpers", "i18n"])

    def test_init_with_custom_titles(self):
        """Test that custom titles override defaults."""
        custom_titles = Titles(titles={"list": "Custom List Title", "custom": "Custom Action Title"})
        self.assertEqual(custom_titles.titles["list"], "Custom List Title")
        self.assertEqual(custom_titles.titles["custom"], "Custom Action Title")
        # Ensure defaults are still present
        self.assertEqual(custom_titles.titles["retrieve"], DEFAULT_TITLES["retrieve"])

    def test_init_with_custom_plugins(self):
        """Test initialization with custom template plugins."""
        custom_plugins = ["custom_plugin", "another_plugin"]
        expected_plugins = ["helpers", "i18n", "custom_plugin", "another_plugin"]
        titles = Titles(template_plugins=custom_plugins)
        self.assertEqual(titles.template_plugins, expected_plugins)

    def test_template_plugins_str(self):
        """Test template plugin string generation."""
        titles = Titles(template_plugins=["plugin1", "plugin2"])
        expected = "{% load helpers %}{% load i18n %}{% load plugin1 %}{% load plugin2 %}"
        self.assertEqual(titles.template_plugins_str, expected)

    def test_render_various_actions_html(self):
        """Test rendering with different action contexts."""
        location_type = LocationType.objects.create(name="Test Location Type Title")
        test_cases = [
            {
                "name": "list_action",
                "context": {"view_action": "list", "verbose_name_plural": "devices"},
                "expected": "Devices",
            },
            {
                "name": "detail_custom_action",
                "context": {
                    "view_action": "custom",
                    "verbose_name_plural": "devices",
                    "detail": True,
                    "object": location_type,
                },
                "expected": "Test Location Type Title",
            },
            {
                "name": "retrieve_action",
                "context": {
                    "view_action": "retrieve",
                    "object": location_type,
                },
                "expected": "Test Location Type Title",
            },
            {
                "name": "create_action",
                "context": {"view_action": "create", "verbose_name": "device"},
                "expected": "Add a new device",
            },
            {
                "name": "update_action",
                "context": {
                    "view_action": "update",
                    "verbose_name": "location type",
                    "object": location_type,
                },
                "expected": "Editing location type Test Location Type Title",
            },
            {
                "name": "destroy_action",
                "context": {"view_action": "destroy", "verbose_name": "device"},
                "expected": "Delete device?",
            },
            {
                "name": "bulk_destroy_action",
                "context": {"view_action": "bulk_destroy", "total_objs_to_delete": 5, "verbose_name_plural": "devices"},
                "expected": "Delete 5 Devices?",
            },
            {
                "name": "bulk_rename_action",
                "context": {
                    "view_action": "bulk_rename",
                    "selected_objects": ["obj1", "obj2", "obj3"],
                    "verbose_name_plural": "devices",
                    "parent_name": "Site A",
                },
                "expected": "Renaming 3 Devices on Site A",
            },
            {
                "name": "bulk_update_action",
                "context": {"view_action": "bulk_update", "objs_count": 10, "verbose_name_plural": "devices"},
                "expected": "Editing 10 Devices",
            },
            {
                "name": "approve_action",
                "context": {"view_action": "approve", "verbose_name": "device"},
                "expected": "Approve Device?",
            },
            {
                "name": "deny_action",
                "context": {"view_action": "deny", "verbose_name": "device"},
                "expected": "Deny Device?",
            },
        ]

        for test_case in test_cases:
            with self.subTest(action=test_case["name"]):
                context = Context(test_case["context"])
                result = self.titles.render(context)
                self.assertEqual(result, test_case["expected"])

    def test_render_various_actions_plain(self):
        """Rendering with mode='plain' returns stripped (text-only) output."""
        context = Context({"view_action": "list", "verbose_name_plural": "devices"})
        self.titles.titles["list"] = "<strong>{{ verbose_name_plural|bettertitle }}</strong>"
        result = self.titles.render(context, mode="plain")
        self.assertEqual(result, "Devices")

        # Also test complex HTML stripping
        self.titles.titles["list"] = '<div class="title"><span>{{ verbose_name_plural|bettertitle }}</span></div>'
        result = self.titles.render(context, mode="plain")
        self.assertEqual(result, "Devices")

    def test_render_with_missing_action(self):
        """Test rendering with an action that doesn't exist in titles."""
        context = Context({"view_action": "nonexistent"})
        result = self.titles.render(context)
        self.assertEqual(result, "")

    def test_render_default_action(self):
        """Test rendering when no view_action is provided."""
        context = Context({"verbose_name_plural": "devices"})
        result = self.titles.render(context)
        self.assertEqual(result, "Devices")  # Should use * action as default

    def test_get_extra_context(self):
        """Test that get_extra_context returns empty dict by default."""
        context = Context({})
        extra_context = self.titles.get_extra_context(context)
        self.assertEqual(extra_context, {})

    def test_get_extra_context_is_used_during_render(self):
        """Test that get_extra_context is being used to extend the context."""
        context = Context({"view_action": "list"})

        class TitlesSubClass(Titles):
            def get_extra_context(self, context: Context) -> dict:
                return {"verbose_name_plural": "devices"}

        rendered_title = TitlesSubClass().render(context)
        self.assertEqual(rendered_title, "Devices")


class TitlesTranslationTestCase(TestCase):
    """
    The prose in `DEFAULT_TITLES` must be translatable, and must stay extractable.

    Those title templates are Django template strings held in a Python literal. `makemessages`
    cannot see `{% blocktrans %}` inside a Python string, so the same messages are declared
    separately with `gettext_noop` in `TRANSLATABLE_TITLE_MESSAGES`. These tests are what stop the
    two drifting apart.
    """

    # Maps each translatable title template to the msgid it should produce.
    EXPECTED_MSGIDS = {
        "destroy": "Delete %(verbose_name)s?",
        "create": "Add a new %(verbose_name)s",
        "update": "Editing %(verbose_name)s %(object)s",
        "bulk_destroy": "Delete %(count)s %(verbose_name_plural)s?",
        "bulk_rename": "Renaming %(count)s %(verbose_name_plural)s on %(parent_name)s",
        "bulk_update": "Editing %(count)s %(verbose_name_plural)s",
        "approve": "Approve %(verbose_name)s?",
        "deny": "Deny %(verbose_name)s?",
    }

    def test_translatable_titles_are_extractable(self):
        """Every blocktrans msgid in DEFAULT_TITLES must also be declared for extraction."""
        for action, msgid in self.EXPECTED_MSGIDS.items():
            with self.subTest(action=action):
                self.assertIn(
                    msgid,
                    TRANSLATABLE_TITLE_MESSAGES,
                    f"the {action!r} title renders msgid {msgid!r}, which is not declared in "
                    "TRANSLATABLE_TITLE_MESSAGES and would therefore never be extracted",
                )

    def test_no_stale_extraction_declarations(self):
        """And nothing declared for extraction should be unreachable from a title."""
        for msgid in TRANSLATABLE_TITLE_MESSAGES:
            with self.subTest(msgid=msgid):
                self.assertIn(msgid, self.EXPECTED_MSGIDS.values())

    def test_every_prose_title_is_wrapped(self):
        """A title containing prose must go through blocktrans, not render English directly."""
        for action, template in DEFAULT_TITLES.items():
            with self.subTest(action=action):
                # Remove whole blocktrans blocks (tag, body, and closing tag), then any remaining
                # tags and variables. Whatever letters survive are prose rendered untranslated.
                bare = re.sub(r"{%\s*blocktrans.*?{%\s*endblocktrans\s*%}", "", template, flags=re.S)
                bare = re.sub(r"{%.*?%}|{{.*?}}", "", bare)
                if re.search(r"[A-Za-z]", bare):
                    self.fail(f"the {action!r} title has untranslated prose outside blocktrans: {bare.strip()!r}")

    def test_titles_render_translated(self):
        """End-to-end: the rendered title actually changes with the active language."""
        titles = Titles()
        context = Context({"view_action": "create", "verbose_name": "device"})
        with translation.override("en"):
            english = titles.render(context, mode="plain")
        self.assertEqual(english, "Add a new device")

        # Uses Nautobot's own catalog, so this asserts the message really is registered.
        with translation.override("de"):
            german = titles.render(Context({"view_action": "create", "verbose_name": "Gerät"}), mode="plain")
        self.assertNotEqual(german, "Add a new Gerät")
        self.assertIn("Gerät", german)
