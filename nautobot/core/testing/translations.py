"""Reusable integrity tests for translation catalogs, for Nautobot core and for Apps alike."""

import gettext
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from django.utils.translation import to_locale

__all__ = ("TranslationCatalogTestCaseMixin",)


def read_catalog(path):
    """Return the message catalog compiled into a `.mo` file."""
    with path.open("rb") as handle:
        return gettext.GNUTranslations(handle)._catalog


class TranslationCatalogTestCaseMixin:
    """
    Assert that a `locale/` directory's compiled catalogs are present, current, and well-formed.

    Mix into a `TestCase` and point `locale_path` at the directory holding `<locale>/LC_MESSAGES/`.
    An App ships that directory inside its package, so:

        from nautobot.apps.testing import TestCase, TranslationCatalogTestCaseMixin

        class MyAppTranslationTestCase(TranslationCatalogTestCaseMixin, TestCase):
            locale_path = Path(__file__).resolve().parent.parent / "locale"

    The checks exist because `.po` and `.mo` drift silently. Django reads only `.mo`, so an edited
    `.po` that was never recompiled keeps serving the old text with nothing to indicate it, and a
    `.mo` missing from the built wheel is indistinguishable at runtime from having no translations.

    A `(language, domain)` pair with no `.po` is skipped rather than failed: an App that has no
    JavaScript strings legitimately ships no `djangojs` catalog. `test_locale_path_contains_catalogs`
    is what stops that leniency turning a mistyped `locale_path` into a suite that passes vacuously.
    """

    #: Directory containing `<locale>/LC_MESSAGES/<domain>.po`. Required.
    locale_path = None
    #: Language codes to check. `None` discovers every locale present in `locale_path`.
    languages = None
    #: Message domains to check, when a source catalog for them exists.
    domains = ("django", "djangojs")

    def _locale_path(self):
        self.assertIsNotNone(self.locale_path, "set `locale_path` to your locale directory")
        return Path(self.locale_path)

    def _languages(self):
        if self.languages is not None:
            return list(self.languages)
        root = self._locale_path()
        if not root.is_dir():
            return []
        return sorted(child.name for child in root.iterdir() if (child / "LC_MESSAGES").is_dir())

    def catalog_path(self, language, domain, suffix):
        return self._locale_path() / to_locale(language) / "LC_MESSAGES" / f"{domain}.{suffix}"

    def _existing_catalogs(self):
        """Yield `(language, domain)` for every pair that has a `.po` source."""
        for language in self._languages():
            for domain in self.domains:
                if self.catalog_path(language, domain, "po").is_file():
                    yield language, domain

    def test_locale_path_contains_catalogs(self):
        """
        `locale_path` must actually contain catalogs.

        Every other check here skips what is absent, so without this a typo in `locale_path` -- or a
        `locale/` directory left out of the built package -- would produce a green suite that proves
        nothing.
        """
        root = self._locale_path()
        self.assertTrue(root.is_dir(), f"{root} is not a directory")
        found = list(self._existing_catalogs())
        self.assertNotEqual(found, [], f"{root} contains no `<locale>/LC_MESSAGES/<domain>.po` files")

    def test_every_catalog_is_compiled(self):
        """
        A `.po` with no `.mo` beside it silently falls back to English for every string.

        Django reads `.mo` and never `.po`, so a missing compiled catalog is indistinguishable at
        runtime from having no translations at all.
        """
        for language, domain in self._existing_catalogs():
            with self.subTest(language=language, domain=domain):
                path = self.catalog_path(language, domain, "mo")
                self.assertTrue(path.is_file(), f"{path} is missing; run `compilemessages`")
                # The header entry is keyed by the empty msgid and is always present, so a catalog
                # of exactly one entry is a compiled-but-empty catalog.
                self.assertGreater(len(read_catalog(path)), 1, f"{path} contains no translations")

    def test_compiled_catalogs_match_their_sources(self):
        """
        Every `.mo` must be the current compilation of its `.po`.

        Recompiles each source into a temporary file and compares catalogs, rather than comparing
        bytes or timestamps: `msgfmt` output is not reproducible across versions, and Git does not
        preserve mtimes, so both of those would fail spuriously.
        """
        msgfmt = shutil.which("msgfmt")
        if msgfmt is None:
            self.skipTest("gettext `msgfmt` is not installed")

        for language, domain in self._existing_catalogs():
            with self.subTest(language=language, domain=domain):
                source = self.catalog_path(language, domain, "po")
                compiled = self.catalog_path(language, domain, "mo")
                self.assertTrue(compiled.is_file(), f"{compiled} is missing; run `compilemessages`")
                with tempfile.TemporaryDirectory() as directory:
                    fresh = Path(directory) / f"{domain}.mo"
                    # argv is the resolved `msgfmt` path plus paths built from `locale_path`; none
                    # of it is caller-supplied.
                    subprocess.run([msgfmt, "--check", "-o", str(fresh), str(source)], check=True)  # noqa: S603
                    self.assertEqual(
                        read_catalog(compiled),
                        read_catalog(fresh),
                        f"{compiled} is stale relative to {source}; run `compilemessages`",
                    )

    def test_plural_entries_declare_the_right_number_of_forms(self):
        """
        Every plural entry must carry exactly as many forms as its catalog declares.

        `nplurals` is not the same everywhere -- Chinese declares one form, German and French two,
        Spanish three -- so a plural entry copied between catalogs can easily end up with the wrong
        count. `msgfmt` does not flag a surplus form while it is still empty, which is exactly the
        state a half-finished translation is in, so the mismatch survives until someone fills it in.
        """
        for language, domain in self._existing_catalogs():
            source = self.catalog_path(language, domain, "po")
            text = source.read_text(encoding="utf-8")
            declared = re.search(r"nplurals=(\d+)", text.split("\n\n", 1)[0])
            self.assertIsNotNone(declared, f"{source} declares no Plural-Forms header")
            expected = int(declared.group(1))
            for block in text.split("\n\n"):
                if not re.search(r"^msgid_plural ", block, re.M):
                    continue
                msgid = re.search(r'^msgid "(.*)"$', block, re.M)
                forms = re.findall(r"^msgstr\[(\d+)\] ", block, re.M)
                with self.subTest(language=language, domain=domain, msgid=msgid.group(1)):
                    self.assertEqual(
                        len(forms),
                        expected,
                        f"{source}: {msgid.group(1)!r} has {len(forms)} plural forms, "
                        f"but the catalog declares nplurals={expected}",
                    )
