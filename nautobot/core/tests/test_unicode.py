"""
Tests that Nautobot actually stores, round-trips, and derives keys from international text.

The gap analysis found that the existing suite could not catch any of the UTF-8 defects it
identified: the one "unicode" model test used 3-byte CJK (`台灣`), which passes on a `utf8mb3`
MySQL database, so the `utf8mb4` requirement was enforced by exactly zero tests. These are the
tests that keep the Phase 0 fixes fixed.
"""

import codecs
import csv
import io

from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from nautobot.core.models.fields import slugify_dashes_to_underscores, slugify_dots_to_dashes
from nautobot.core.testing import APITestCase, TestCase
from nautobot.dcim.models import Location, LocationType
from nautobot.extras.choices import CustomFieldTypeChoices
from nautobot.extras.models import CustomField, Status, Tag

# 4-byte UTF-8. This is the only kind of character that actually exercises utf8mb4: everything in
# the Basic Multilingual Plane, including ordinary CJK, fits in 3 bytes and stores fine on utf8mb3.
EMOJI = "🎉"
CJK_EXTENSION_B = "𠀋"  # U+2000B, a 4-byte CJK ideograph

# 3-byte and 2-byte samples across scripts, for the key-derivation matrix.
CHINESE = "設備名稱"
JAPANESE = "データセンター"
CYRILLIC = "Москва"
ACCENTED = "Standort München"


class FourByteCharacterStorageTest(TestCase):
    """
    A 4-byte character must survive a write/read round trip.

    On a `utf8mb3` MySQL database these raise at INSERT time, which is exactly the failure the
    startup system check now warns about. If this test fails, the database is misconfigured.
    """

    def test_emoji_in_char_field(self):
        tag = Tag.objects.create(name=EMOJI)
        tag.refresh_from_db()
        self.assertEqual(tag.name, EMOJI)

    def test_emoji_in_text_field(self):
        tag = Tag.objects.create(name="Emoji description test", description=f"party {EMOJI} time")
        tag.refresh_from_db()
        self.assertEqual(tag.description, f"party {EMOJI} time")

    def test_astral_plane_cjk_in_char_field(self):
        tag = Tag.objects.create(name=CJK_EXTENSION_B)
        tag.refresh_from_db()
        self.assertEqual(tag.name, CJK_EXTENSION_B)

    def test_mixed_scripts_round_trip(self):
        for value in (CHINESE, JAPANESE, CYRILLIC, ACCENTED, f"{EMOJI}{CHINESE}"):
            with self.subTest(value=value):
                tag = Tag.objects.create(name=value)
                tag.refresh_from_db()
                self.assertEqual(tag.name, value)

    def test_max_length_counts_characters_not_bytes(self):
        """A 255-character CJK name is 765 bytes; `max_length` must not reject it."""
        name = CHINESE[0] * 100
        tag = Tag.objects.create(name=name)
        tag.full_clean()
        tag.refresh_from_db()
        self.assertEqual(len(tag.name), 100)


class KeyDerivationTest(TestCase):
    """
    Non-Latin labels must derive meaningful keys.

    Before the Phase 0 fix these all collapsed to `"a"`, so a Japanese-labelled custom field became
    REST field `cf_a`, and a second one became `cf_a_2`, with no warning to the user.
    """

    def test_non_latin_labels_do_not_collapse(self):
        cases = {
            CHINESE: "she_bei_ming_cheng",
            JAPANESE: "tetasenta",
            CYRILLIC: "moskva",
            ACCENTED: "standort_munchen",
        }
        for label, expected in cases.items():
            with self.subTest(label=label):
                self.assertEqual(slugify_dashes_to_underscores(label), expected)

    def test_derived_keys_are_distinct_across_scripts(self):
        """The real defect was collisions, not just ugly keys."""
        keys = {slugify_dashes_to_underscores(label) for label in (CHINESE, JAPANESE, CYRILLIC, ACCENTED)}
        self.assertEqual(len(keys), 4)

    def test_ascii_behavior_is_unchanged(self):
        """Existing installs must keep deriving the same keys they always did."""
        cases = {
            "123 main st": "a123_main_st",
            "Site Name": "site_name",
            "my_field": "my_field",
            "Circuit ID": "circuit_id",
            "UPPER Case": "upper_case",
            "A-B-C": "a_b_c",
        }
        for label, expected in cases.items():
            with self.subTest(label=label):
                self.assertEqual(slugify_dashes_to_underscores(label), expected)

    def test_derived_keys_are_graphql_safe(self):
        """Whatever we derive has to be a legal GraphQL/Python identifier."""
        for label in (CHINESE, JAPANESE, CYRILLIC, ACCENTED, "123 main st", EMOJI, "", "!!!"):
            with self.subTest(label=label):
                key = slugify_dashes_to_underscores(label)
                self.assertTrue(key.isidentifier(), f"{key!r} derived from {label!r} is not an identifier")

    def test_empty_input_does_not_raise(self):
        """`content[0]` used to raise IndexError on empty input."""
        self.assertEqual(slugify_dashes_to_underscores(""), "a")
        self.assertEqual(slugify_dots_to_dashes(""), "")

    def test_custom_field_with_non_latin_label(self):
        """End-to-end: the derived key reaches the database intact and is usable."""
        custom_field = CustomField.objects.create(type=CustomFieldTypeChoices.TYPE_TEXT, label=CHINESE)
        custom_field.content_types.set([ContentType.objects.get_for_model(Location)])
        custom_field.refresh_from_db()
        self.assertEqual(custom_field.label, CHINESE)
        self.assertEqual(custom_field.key, "she_bei_ming_cheng")
        self.assertTrue(custom_field.key.isidentifier())


class NonASCIIAPITest(APITestCase):
    """Creating and finding objects with international names through the REST API."""

    def test_create_with_non_ascii_name(self):
        self.add_permissions("extras.add_tag", "extras.view_tag")
        response = self.client.post(
            reverse("extras-api:tag-list"),
            data={"name": f"{CHINESE}{EMOJI}", "content_types": ["dcim.device"]},
            format="json",
            **self.header,
        )
        self.assertHttpStatus(response, 201)
        self.assertEqual(response.data["name"], f"{CHINESE}{EMOJI}")
        self.assertTrue(Tag.objects.filter(name=f"{CHINESE}{EMOJI}").exists())

    def test_search_finds_non_ascii_name(self):
        self.add_permissions("extras.view_tag")
        Tag.objects.create(name=f"{CHINESE} router")
        response = self.client.get(f"{reverse('extras-api:tag-list')}?q={CHINESE}", **self.header)
        self.assertHttpStatus(response, 200)
        self.assertGreaterEqual(response.data["count"], 1)
        self.assertIn(CHINESE, response.data["results"][0]["name"])


class CSVByteOrderMarkTest(APITestCase):
    """
    The REST API CSV export/import pair must agree about the byte-order mark.

    Previously the export omitted a BOM (so Excel mojibaked every non-ASCII character) while the
    import did not strip one (so a BOM-prefixed file -- including Nautobot's own UI export --
    silently lost its first column, because "﻿id" matches no serializer field).
    """

    def test_export_omits_bom_by_default(self):
        """Programmatic clients decode plain utf-8; a BOM would corrupt their first header."""
        self.add_permissions("extras.view_status")
        response = self.client.get(f"{reverse('extras-api:status-list')}?format=csv", **self.header)
        self.assertHttpStatus(response, 200)
        self.assertFalse(response.content.startswith(codecs.BOM_UTF8))

    def test_export_includes_bom_on_request(self):
        """`?bom=true` is for humans who will open the file in Excel."""
        self.add_permissions("extras.view_status")
        response = self.client.get(f"{reverse('extras-api:status-list')}?format=csv&bom=true", **self.header)
        self.assertHttpStatus(response, 200)
        self.assertTrue(response.content.startswith(codecs.BOM_UTF8))

    def test_export_import_round_trip_preserves_first_column(self):
        self.add_permissions("extras.view_status", "extras.add_status")

        status = Status.objects.create(name=f"{CHINESE} status", description=f"{EMOJI} description")
        status.content_types.set([ContentType.objects.get_for_model(Location)])

        response = self.client.get(f"{reverse('extras-api:status-list')}?format=csv&bom=true", **self.header)
        self.assertHttpStatus(response, 200)
        exported = response.content

        # Feed the exported bytes straight back in, BOM and all.
        rows = list(csv.DictReader(io.StringIO(exported.decode("utf-8-sig"))))
        self.assertIn("id", rows[0], "the BOM must not corrupt the first column header")

        exported_row = next(row for row in rows if row["name"] == f"{CHINESE} status")
        self.assertEqual(exported_row["description"], f"{EMOJI} description")

    def test_import_strips_bom(self):
        """A BOM-prefixed upload must not lose its first column."""
        self.add_permissions("extras.add_tag", "extras.view_tag")
        csv_body = f"name,content_types\n{CHINESE} imported,dcim.device\n"
        response = self.client.post(
            reverse("extras-api:tag-list"),
            data=codecs.BOM_UTF8 + csv_body.encode("utf-8"),
            content_type="text/csv",
            **self.header,
        )
        self.assertHttpStatus(response, 201)
        self.assertTrue(Tag.objects.filter(name=f"{CHINESE} imported").exists())


class NonASCIIUITest(TestCase):
    """Smoke tests that international names render and are searchable through the UI."""

    def test_object_with_non_ascii_name_renders(self):
        self.add_permissions("dcim.view_location")
        location_type = LocationType.objects.create(name=f"{CHINESE} type")
        status = Status.objects.get_for_model(Location).first()
        location = Location.objects.create(name=f"{CHINESE}{EMOJI}", location_type=location_type, status=status)

        response = self.client.get(location.get_absolute_url())
        self.assertBodyContains(response, f"{CHINESE}{EMOJI}")


class SchemaLocaleIndependenceTest(APITestCase):
    """
    The cached OpenAPI schema must not vary with the requesting user's language.

    Model and serializer metadata is translatable, so without pinning, whichever user warmed the
    cache would decide the language of the `description` values served to everyone else -- for a
    week, and under `Cache-Control: public`.
    """

    def test_schema_is_identical_regardless_of_user_language(self):
        from django.core.cache import cache

        descriptions = {}
        for language in ("en", "de", "fr"):
            cache.clear()
            self.user.set_config("language", language, commit=True)
            response = self.client.get("/api/swagger.json?api_version=3.2", **self.header)
            self.assertHttpStatus(response, 200)
            schema = response.data
            descriptions[language] = schema["components"]["schemas"]["Device"]["properties"]["name"].get(
                "description", ""
            )

        self.assertEqual(
            descriptions["en"],
            descriptions["de"],
            "schema description changed with the requesting user's language",
        )
        self.assertEqual(descriptions["en"], descriptions["fr"])
