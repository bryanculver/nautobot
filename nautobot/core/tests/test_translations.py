"""
Integrity tests for the shipped translation catalogs.

Both the `.po` sources and the compiled `.mo` files are tracked in Git, because Django reads only
`.mo` at runtime and we do not want a build step between checkout and working translations. The
cost of that choice is that the two can drift: editing a `.po` without re-running
`invoke compilemessages` leaves the old text being served, with nothing to indicate it. These tests
close that gap.
"""

import gettext
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from django.apps import apps
from django.conf import settings
from django.utils import translation
from django.utils.translation import to_locale

from nautobot.core.testing import TestCase

DOMAINS = ["django", "djangojs"]

# Non-English languages ship catalogs; English is the source language and has none.
NON_ENGLISH_LANGUAGES = [code for code, _ in settings.LANGUAGES if code != "en"]

LOCALE_PATH = Path(settings.LOCALE_PATHS[0])

# `nautobot/core/tests/` -> repo root. Absent when Nautobot is installed from a wheel rather than
# run from a checkout, which the packaging test below accounts for.
PYPROJECT_PATH = Path(__file__).resolve().parents[3] / "pyproject.toml"


def catalog_path(language, domain, suffix):
    return LOCALE_PATH / to_locale(language) / "LC_MESSAGES" / f"{domain}.{suffix}"


def read_catalog(path):
    """Return the message catalog compiled into a `.mo` file."""
    with path.open("rb") as handle:
        return gettext.GNUTranslations(handle)._catalog


class TranslationCatalogTestCase(TestCase):
    def test_every_shipped_language_has_compiled_catalogs(self):
        """
        A language in `LANGUAGES` with no `.mo` silently falls back to English for every string.

        Django reads `.mo` and never `.po`, so a missing or unshipped compiled catalog is
        indistinguishable at runtime from having no translations at all.
        """
        for language in NON_ENGLISH_LANGUAGES:
            for domain in DOMAINS:
                with self.subTest(language=language, domain=domain):
                    path = catalog_path(language, domain, "mo")
                    self.assertTrue(path.is_file(), f"{path} is missing; run `invoke compilemessages`")
                    # The header entry is keyed by the empty msgid and is always present, so a
                    # catalog of exactly one entry is a compiled-but-empty catalog.
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

        for language in NON_ENGLISH_LANGUAGES:
            for domain in DOMAINS:
                with self.subTest(language=language, domain=domain):
                    source = catalog_path(language, domain, "po")
                    compiled = catalog_path(language, domain, "mo")
                    with tempfile.TemporaryDirectory() as directory:
                        fresh = Path(directory) / f"{domain}.mo"
                        # argv is the resolved `msgfmt` path plus paths built from settings and the
                        # constants above; none of it is caller-supplied.
                        subprocess.run([msgfmt, "--check", "-o", str(fresh), str(source)], check=True)  # noqa: S603
                        self.assertEqual(
                            read_catalog(compiled),
                            read_catalog(fresh),
                            f"{compiled} is stale relative to {source}; run `invoke compilemessages`",
                        )

    def test_translations_are_single_line(self):
        """
        No `msgstr` may spread its text across continuation lines.

        The fuzzy-clearing step in `invoke makemessages` empties translations by matching
        `msgstr "..."` and `msgstr[N] "..."` a line at a time. A wrapped translation -- `msgstr ""`
        followed by quoted continuation lines -- would survive that untouched while the `fuzzy`
        marker was stripped, promoting one of msgmerge's guesses into a translation gettext
        actually serves. Exactly that bug shipped once via the plural forms.

        A multi-line *msgid* is fine and does occur, because several source strings contain
        embedded newlines; only the translation side is load-bearing here.
        """
        wrapped = re.compile(r'^(?:msgstr|msgstr\[\d+\]) ""\n"', re.MULTILINE)
        for language in NON_ENGLISH_LANGUAGES:
            for domain in DOMAINS:
                source = catalog_path(language, domain, "po")
                # The header's own msgstr is legitimately multi-line, so skip that first entry.
                text = source.read_text(encoding="utf-8")
                body = text.split("\n\n", 1)[1] if "\n\n" in text else ""
                with self.subTest(language=language, domain=domain):
                    self.assertIsNone(
                        wrapped.search(body),
                        f"{source} wraps a translation across lines, which the fuzzy-clearing step "
                        "in `invoke makemessages` cannot empty",
                    )

    def test_plural_entries_declare_the_right_number_of_forms(self):
        """
        Every plural entry must carry exactly as many forms as its catalog declares.

        `nplurals` is not the same everywhere -- Chinese declares one form, German and French two,
        Spanish three -- so a plural entry copied between catalogs can easily end up with the wrong
        count. `msgfmt` does not flag a surplus form while it is still empty, which is exactly the
        state a half-finished translation is in, so the mismatch survives until someone fills it in.
        """
        for language in NON_ENGLISH_LANGUAGES:
            for domain in DOMAINS:
                source = catalog_path(language, domain, "po")
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

    def test_compiled_catalogs_are_packaged(self):
        """
        The compiled catalogs must be declared for distribution.

        Poetry includes tracked source files by default but not build outputs, so without an
        explicit `include` the published wheel carries `.po` files Django never reads and no
        translations at all -- a failure that no test of the source tree would catch.
        """
        if not PYPROJECT_PATH.is_file():
            self.skipTest("not running from a source checkout")

        include = re.search(
            r'^\s*\{\s*path\s*=\s*"nautobot/locale/\*\*/\*\.mo"\s*,\s*format\s*=\s*\[(?P<formats>[^]]*)\]',
            PYPROJECT_PATH.read_text(encoding="utf-8"),
            re.MULTILINE,
        )
        self.assertIsNotNone(include, "pyproject.toml does not include nautobot/locale/**/*.mo")
        for distribution in ("sdist", "wheel"):
            with self.subTest(distribution):
                self.assertIn(distribution, include.group("formats"))


class ModelVerboseNameTestCase(TestCase):
    """Guard the interaction between translated model names and Django's plural derivation."""

    def test_translated_verbose_name_requires_explicit_plural(self):
        """
        A model whose `verbose_name` is translated must declare `verbose_name_plural` too.

        When `verbose_name_plural` is not set, Django derives it as `verbose_name + "s"`. That is
        correct for untranslated English, but if the singular is translated the "s" is appended to
        the *translated* text: "Gruppe" becomes "Gruppes" rather than "Gruppen", and Chinese "组"
        becomes "组s". The result is visible in page titles, table headers, and delete
        confirmations, and nothing else catches it -- the catalogs are valid, and English is fine.

        Declaring the plural costs an `AlterModelOptions` migration, so models that cannot take one
        yet must leave the singular untranslated rather than ship a mangled plural.
        """
        offenders = []
        for model in apps.get_models():
            meta = model._meta
            if "verbose_name" not in meta.original_attrs or "verbose_name_plural" in meta.original_attrs:
                continue
            with translation.override("en"):
                english = str(meta.verbose_name)
            for language in NON_ENGLISH_LANGUAGES:
                with translation.override(language):
                    if str(meta.verbose_name) != english:
                        offenders.append(
                            f"{meta.app_label}.{model.__name__} renders {str(meta.verbose_name_plural)!r} in {language}"
                        )
                        break

        self.assertEqual(
            offenders,
            [],
            "these models translate verbose_name but let Django derive verbose_name_plural, which "
            "appends 's' to the translated singular; declare verbose_name_plural explicitly or "
            "leave verbose_name untranslated:\n  " + "\n  ".join(offenders),
        )


class PluralizationTestCase(TestCase):
    """Guard against pluralisation that only works in English."""

    #: Directories whose contents are not product surface, or are not ours.
    SKIP = ("node_modules", "project-static", "/tests/", "/migrations/")

    #: `{{ n }} item{{ n|pluralize }}` -- the suffix never reaches gettext.
    TEMPLATE_PLURALIZE = re.compile(r"\|\s*pluralize")

    #: `f"{n} item{'s' if n != 1 else ''}"` and Django's `pluralize()` helper used in Python.
    PYTHON_PLURAL_HACKS = (
        re.compile(r"""['\"]s['\"]\s+if\s+\w+\s*[!=]=\s*1"""),
        re.compile(r"""\bif\s+\w+\s*[!=]=\s*1\s+else\s+['\"]s['\"]"""),
        re.compile(r"\bpluralize\("),
    )

    def _source_files(self, suffix):
        root = PYPROJECT_PATH.parent / "nautobot"
        if not root.is_dir():
            self.skipTest("not running from a source checkout")
        for path in sorted(root.rglob(f"*{suffix}")):
            if any(skip in str(path) for skip in self.SKIP):
                continue
            yield path

    def test_templates_do_not_use_the_pluralize_filter(self):
        """
        Templates must express counts with `{% blocktrans count %}`, not `|pluralize`.

        `|pluralize` appends "s" outside the translation, so the suffix never reaches the catalog:
        a translator sees `%(count)s device` with no way to supply a plural form, and the rendered
        German reads "5 Gerats". Languages are not limited to two forms either -- Spanish declares
        three and Chinese one -- which a boolean suffix cannot express at all.
        """
        offenders = []
        for path in self._source_files(".html"):
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if self.TEMPLATE_PLURALIZE.search(line):
                    offenders.append(f"{path}:{number}: {line.strip()}")
        self.assertEqual(
            offenders,
            [],
            "Use {% blocktrans count n=value %}...{% plural %}...{% endblocktrans %} instead of "
            "the |pluralize filter:\n" + "\n".join(offenders),
        )

    def test_python_does_not_hand_roll_plurals(self):
        """
        Python must express counts with `ngettext`, not by appending "s".

        Same reasoning as the template case: the choice has to be made *inside* gettext so the
        catalog can carry one form per language, and so gettext can apply that language's own
        plural rule. The rules genuinely differ -- French counts zero as singular (`n > 1`) while
        German counts it as plural (`n != 1`) -- so no amount of English-side branching is correct
        everywhere.
        """
        offenders = []
        for path in self._source_files(".py"):
            if path.name == Path(__file__).name:
                continue  # this file names the patterns it forbids
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if any(pattern.search(line) for pattern in self.PYTHON_PLURAL_HACKS):
                    offenders.append(f"{path}:{number}: {line.strip()}")
        self.assertEqual(
            offenders,
            [],
            "Use ngettext(singular, plural, count) instead of appending 's':\n" + "\n".join(offenders),
        )
