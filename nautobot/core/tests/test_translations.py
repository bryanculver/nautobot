"""
Integrity tests for the shipped translation catalogs.

Both the `.po` sources and the compiled `.mo` files are tracked in Git, because Django reads only
`.mo` at runtime and we do not want a build step between checkout and working translations. The
cost of that choice is that the two can drift: editing a `.po` without re-running
`invoke compilemessages` leaves the old text being served, with nothing to indicate it. These tests
close that gap.
"""

import ast
import contextlib
from pathlib import Path
import re
import subprocess
import sys
import tempfile

from django.apps import apps
from django.conf import settings
from django.urls import resolve, reverse
from django.utils import translation
from django.utils.translation import to_locale
from django.utils.translation.trans_real import all_locale_paths, DjangoTranslation

from nautobot.core.testing import TestCase
from nautobot.core.testing.translations import TranslationCatalogTestCaseMixin

DOMAINS = ["django", "djangojs"]

# Non-English languages ship catalogs; English is the source language and has none.
NON_ENGLISH_LANGUAGES = [code for code, _ in settings.LANGUAGES if code != "en"]

LOCALE_PATH = Path(settings.LOCALE_PATHS[0])

# `nautobot/core/tests/` -> repo root. Absent when Nautobot is installed from a wheel rather than
# run from a checkout, which the packaging test below accounts for.
PYPROJECT_PATH = Path(__file__).resolve().parents[3] / "pyproject.toml"


class TranslationCatalogTestCase(TranslationCatalogTestCaseMixin, TestCase):
    """Nautobot's own shipped catalogs, checked with the same mixin Apps use."""

    locale_path = LOCALE_PATH
    languages = NON_ENGLISH_LANGUAGES
    domains = DOMAINS

    def test_fuzzy_clearing_empties_every_translation_shape(self):
        """
        `invoke makemessages` must be able to empty any translation msgmerge guessed.

        gettext ignores a fuzzy entry at runtime, so a guess renders as English while *looking*
        translated in the catalog -- the worst state for anyone auditing coverage. The clearing step
        therefore strips the marker and empties the text together; if it ever emptied only part of a
        translation, the leftover guess would be promoted from ignored to served.

        This exercises the script `tasks.py` actually emits, against every entry shape a catalog
        contains: a translation wrapped across continuation lines (which happens whenever a msgid
        holds embedded newlines, `--no-wrap` notwithstanding), a plural with one form per language,
        a plain single-line entry, and the header -- which is itself flagged fuzzy and whose charset
        declaration must survive, or the catalog stops compiling.
        """
        tasks_path = PYPROJECT_PATH.parent / "tasks.py"
        if not tasks_path.is_file():
            self.skipTest("not running from a source checkout")

        script = None
        for node in ast.walk(ast.parse(tasks_path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.FunctionDef) and node.name == "_clear_fuzzy_translations":
                for sub in ast.walk(node):
                    if isinstance(sub, ast.Assign) and getattr(sub.targets[0], "id", None) == "script":
                        script = ast.literal_eval(sub.value)
        self.assertIsNotNone(script, "could not find the clearing script in tasks.py")

        sample = (
            "#, fuzzy\n"
            'msgid ""\n'
            '"Help text. Example:\\n"\n'
            '"<pre>{}</pre>"\n'
            'msgstr ""\n'
            '"Falsche Vermutung. Beispiel:\\n"\n'
            '"<pre>{}</pre>"\n'
            "\n"
            "#, fuzzy\n"
            '#| msgid "%(count)s widget"\n'
            'msgid "%(count)s interface"\n'
            'msgid_plural "%(count)s interfaces"\n'
            'msgstr[0] "Falsche Vermutung"\n'
            'msgstr[1] "Falsche Vermutungen"\n'
            "\n"
            "#, fuzzy\n"
            'msgid "Cable"\n'
            'msgstr "Kabel raten"\n'
            "\n"
            'msgid "Kept"\n'
            'msgstr "Behalten"\n'
        )
        header = '#, fuzzy\nmsgid ""\nmsgstr ""\n"Content-Type: text/plain; charset=UTF-8\\n"\n\n'

        with tempfile.TemporaryDirectory() as workspace:
            catalog = Path(workspace) / "nautobot" / "locale" / "xx" / "LC_MESSAGES" / "django.po"
            catalog.parent.mkdir(parents=True)
            catalog.write_text(header + sample, encoding="utf-8")
            # Run it the way `tasks.py` does -- `python -c` in the repo root -- rather than
            # exec()ing it in-process, so the test exercises the real invocation.
            completed = subprocess.run(  # noqa: S603  # the script is our own tasks.py source
                [sys.executable, "-c", script],
                cwd=workspace,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            result = catalog.read_text(encoding="utf-8")

        self.assertNotIn("Falsche Vermutung", result, "a guessed translation survived clearing")
        self.assertNotIn("Kabel raten", result, "a single-line guess survived clearing")
        self.assertIn('msgstr[0] ""', result, "plural form 0 was not emptied")
        self.assertIn('msgstr[1] ""', result, "plural form 1 was not emptied")
        self.assertIn('"<pre>{}</pre>"', result, "the msgid lost its continuation lines")
        self.assertIn('"Behalten"', result, "a non-fuzzy translation was cleared")
        self.assertIn("charset=UTF-8", result, "the header lost its charset declaration")
        self.assertEqual(result.count("#, fuzzy"), 1, "only the header should keep a fuzzy marker")

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


class AppTranslationContractTestCase(TestCase):
    """Guard the contract that lets separately-packaged Apps ship their own catalogs."""

    def test_installed_app_locale_directories_are_discovered(self):
        """
        Every installed app that ships a `locale/` directory must be on the search path.

        This is what makes the App contract work: Django's `all_locale_paths()` appends
        `<app>/locale` for each entry in `INSTALLED_APPS`, and Nautobot appends every `PLUGINS`
        entry there. The assertion is over the mechanism rather than a named app, so it still holds
        in a deployment with no Apps installed.
        """
        searched = {Path(entry) for entry in all_locale_paths()}
        expected = [
            Path(config.path) / "locale" for config in apps.get_app_configs() if (Path(config.path) / "locale").is_dir()
        ]
        self.assertNotEqual(expected, [], "no installed app ships a locale directory; test is vacuous")
        for locale_dir in expected:
            with self.subTest(locale_dir=str(locale_dir)):
                self.assertIn(locale_dir, searched)

    def test_javascript_catalog_is_not_restricted_to_a_package(self):
        """
        The `/jsi18n/` route must not name any `packages`.

        `JavaScriptCatalog` treats `packages` as a *restriction*, not an addition -- naming one
        excludes every other installed app, which is exactly how an App supplies JavaScript strings.
        It also silently excluded `django.contrib.admin`'s own catalog. Asserted structurally so it
        holds even where no App is installed.
        """
        view = resolve(reverse("javascript_catalog")).func
        self.assertEqual(
            getattr(view, "view_initkwargs", {}),
            {},
            "the jsi18n route must not pass `packages=`; doing so excludes App catalogs",
        )

    def test_javascript_plural_rule_covers_our_plural_entries(self):
        """
        The plural rule served to JavaScript must be able to index our own plural forms.

        `DjangoTranslation.merge()` takes the plural function from the *first* catalog merged, and
        with no `packages=` restriction that is some other installed app's -- `django.contrib.admin`
        declares `nplurals=3` for French where Nautobot declares 2. Harmless while our `djangojs`
        catalogs contain no plural entries, which is the case today, so this guards the moment that
        stops being true rather than asserting a rule we do not own.
        """
        for language in NON_ENGLISH_LANGUAGES:
            source = self.catalog_path_for(language)
            if not source.is_file():
                continue
            forms = len(re.findall(r"^msgstr\[\d+\] ", source.read_text(encoding="utf-8"), re.M))
            if not forms:
                continue  # no JS plurals yet; nothing the served rule could get wrong
            served = DjangoTranslation(language, domain="djangojs", localedirs=None)
            reachable = {served.plural(n) for n in range(0, 1000)}
            declared = int(re.search(r"nplurals=(\d+)", source.read_text(encoding="utf-8")).group(1))
            with self.subTest(language=language):
                self.assertTrue(
                    max(reachable) < declared,
                    f"the plural rule served for {language} reaches form index {max(reachable)}, but "
                    f"nautobot/locale/{to_locale(language)}/LC_MESSAGES/djangojs.po declares only "
                    f"{declared} forms. Another installed app's catalog is supplying the rule.",
                )

    def catalog_path_for(self, language):
        return LOCALE_PATH / to_locale(language) / "LC_MESSAGES" / "djangojs.po"


class EmbeddedTemplateStringTestCase(TestCase):
    """Guard the strings that live in template fragments held in Python string literals."""

    def test_template_tags_embedded_in_python_are_extractable(self):
        """
        Every `{% trans %}` written inside a Python string literal must reach the catalog.

        `makemessages` runs the Python extractor over `.py` files -- it looks for `gettext()` calls,
        not for template syntax -- and the Django template extractor only over `.html`. A
        `{% trans %}` inside a Python string is therefore invisible to both. Nothing breaks: gettext
        falls back to the msgid, so the fragment renders in English and keeps rendering in English
        in every language, with no entry a translator could ever fill in. That silence is the whole
        reason for this test.

        `django-tables2` fragments are the usual home for these, because a table column's markup is
        conventionally written beside the table class rather than in its own template file. The fix
        is to declare the msgids next to the fragment with `gettext_noop()`, which the Python
        extractor does see -- see `TRANSLATABLE_IPADDRESS_OR_RANGE_ACTIONS` in `nautobot.ipam.tables`.
        """
        catalog = set(
            re.findall(
                r'^msgid "(.*)"$',
                (LOCALE_PATH / "de" / "LC_MESSAGES" / "django.po").read_text(encoding="utf-8"),
                re.M,
            )
        )
        self.assertNotEqual(catalog, set(), "the German catalog is empty; the check below would pass vacuously")

        tag = re.compile(r"\{%\s*(?:trans|translate)\s+\"([^\"]+)\"")
        unreachable = []
        for path in sorted(Path(settings.BASE_DIR).rglob("*.py")):
            if "/tests/" in str(path) or "/migrations/" in str(path):
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for match in tag.finditer(text):
                if match.group(1) not in catalog:
                    line = text[: match.start()].count("\n") + 1
                    unreachable.append(f"{path.relative_to(settings.BASE_DIR)}:{line}: {match.group(1)!r}")

        self.assertEqual(
            unreachable,
            [],
            "these strings are marked for translation but no extractor can see them, so they will "
            "render in English forever. Declare each one with `gettext_noop()` beside its fragment:\n"
            + "\n".join(unreachable),
        )


class LazyHelpTextTestCase(TestCase):
    """Guard help text that is assembled at field-construction time."""

    def test_comment_field_help_text_is_not_frozen_at_import(self):
        """
        `CommentField`'s help text must resolve per request, not once at startup.

        `format_html()` resolves a `gettext_lazy` argument immediately, and `CommentField.__init__`
        reads `default_helptext` when the field is *constructed* -- which, for a field declared in a
        form class body, is import time. Building it eagerly froze the text in whatever language was
        active during startup, so every user saw English regardless of their preference, on all 127
        comment and note fields in the product.

        Nothing about that failure is visible in isolation: the string is marked, its msgids are
        translated, and the catalog checks all pass. Only comparing two languages in one process
        reveals it, which is what this test does.
        """
        # Deliberately a *product* form rather than a bare `CommentField()`: the field instance
        # inside `NoteForm` was constructed when its module was imported, which is precisely the
        # situation that froze the text. A `CommentField()` built inside this test would resolve
        # under the active language whether or not the bug is present, and the test would pass
        # vacuously.
        from nautobot.extras.forms.forms import NoteForm

        rendered = {}
        for language in ("en", "de", "fr"):
            with translation.override(language):
                rendered[language] = str(NoteForm().fields["note"].help_text)

        self.assertNotEqual(
            rendered["de"],
            rendered["en"],
            "CommentField help text is identical in German and English; it is being resolved once "
            "instead of per request (see `_markdown_helptext` in `nautobot.core.forms.fields`)",
        )
        self.assertNotEqual(rendered["fr"], rendered["de"])

    def test_comment_field_help_text_is_still_marked_safe(self):
        """
        The deferred help text must keep `__html__`, or its markup renders as visible tags.

        Wrapping the builder in `lazy()` is only correct if `SafeString` is given as the result
        class; with `str` the proxy loses `__html__` and the anchor elements would be escaped into
        the page as literal `&lt;a href=...&gt;` text.
        """
        from django.utils.html import conditional_escape

        from nautobot.extras.forms.forms import NoteForm

        with translation.override("de"):
            help_text = NoteForm().fields["note"].help_text
            self.assertTrue(hasattr(help_text, "__html__"), "help text lost its `__html__` marker")
            self.assertNotIn("&lt;", conditional_escape(help_text), "help text markup would be escaped")


class FrozenTranslationTestCase(TestCase):
    """Guard against text that is marked and translated, yet still renders in one fixed language."""

    #: Labels that are knowingly still English, with the reason each is out of reach here.
    KNOWN_EXCEPTIONS = {
        # Resolved from the *model's* `Meta.verbose_name` through the cable fieldset. Translating
        # those needs `AlterModelOptions` migrations and is a separate, deliberate decision.
        "Device",
        "Interface",
    }

    def _translated_msgids(self):
        source = Path(settings.LOCALE_PATHS[0]) / "de" / "LC_MESSAGES" / "django.po"
        catalog = set()
        for block in source.read_text(encoding="utf-8").split("\n\n"):
            msgid = re.search(r'^msgid "(.+)"$', block, re.M)
            if msgid and re.search(r'^msgstr "(.+)"$', block, re.M):
                catalog.add(msgid.group(1).replace('\\"', '"'))
        return catalog

    def test_no_form_label_or_help_text_is_frozen(self):
        """
        A plain `str` whose text is a *translated* msgid was resolved once and kept.

        This is the failure mode that survives every other check in this module: the string is
        marked, the catalog has a translation for it, `msgfmt` is happy -- and the user still sees
        English, because a `gettext` call was evaluated eagerly (typically by `format_html()` at
        import time) and the resulting `str` cannot vary by request.

        The two bugs this caught were `CommentField.default_helptext` and
        `CustomFieldDescriptionField.default_helptext`, each affecting every comment and note field
        in the product.
        """
        import importlib
        import pkgutil

        from django import forms
        from django.utils.functional import Promise

        import nautobot as nautobot_package

        catalog = self._translated_msgids()
        self.assertNotEqual(catalog, set(), "no translated msgids found; this check would pass vacuously")

        modules = []
        for info in pkgutil.walk_packages(nautobot_package.__path__, prefix="nautobot."):
            name = info.name
            if ".tests" in name or ".migrations" in name or "test_jobs" in name:
                continue
            if not (name.endswith(".forms") or ".forms." in name):
                continue
            with contextlib.suppress(Exception):
                modules.append(importlib.import_module(name))

        tag = re.compile(r"<[^>]+>")
        frozen = []
        seen = set()
        for module in modules:
            for attr in dir(module):
                obj = getattr(module, attr, None)
                if not isinstance(obj, type) or not issubclass(obj, forms.BaseForm):
                    continue
                key = f"{obj.__module__}.{obj.__name__}"
                if key in seen or obj.__module__.startswith(("django", "example_app")):
                    continue
                seen.add(key)
                model = getattr(getattr(obj, "_meta", None), "model", None)
                instance = None
                for args in ((), (model,) if model is not None else None):
                    if args is None:
                        continue
                    with contextlib.suppress(Exception):
                        instance = obj(*args)
                        break
                if instance is None:
                    continue
                for field_name, field in instance.fields.items():
                    # App-contributed fields (custom fields, table extensions) belong to the App.
                    if field_name.startswith("cf_") or "example_app" in field_name:
                        continue
                    for value in (field.label, field.help_text):
                        if isinstance(value, Promise) or not isinstance(value, str) or not value.strip():
                            continue
                        plain = " ".join(tag.sub(" ", value).split())
                        if plain in self.KNOWN_EXCEPTIONS:
                            continue
                        # Exact match catches a frozen label. Substring match is what catches a
                        # frozen *sentence*: `CommentField`'s help text interpolates two anchors, so
                        # the rendered string never equals its msgid -- only the translated fragments
                        # inside it do. Checking exact-only silently missed that bug.
                        hit = (
                            plain
                            if plain in catalog
                            else next((msgid for msgid in catalog if len(msgid) > 20 and msgid in plain), None)
                        )
                        if hit is not None:
                            frozen.append(f"{key}.{field_name}: {hit!r}")

        self.assertEqual(
            sorted(set(frozen)),
            [],
            "these strings have a translation in the catalog but are stored as plain `str`, so they "
            "render in one fixed language for every user. Defer the `gettext` call (see "
            "`_markdown_helptext` in `nautobot.core.forms.fields`) or mark the underlying "
            "`verbose_name`:\n" + "\n".join(sorted(set(frozen))),
        )

    def test_no_table_column_header_is_frozen(self):
        """
        The same check for `django-tables2` column headers.

        Table headers reach the user through a different path than form labels -- `Column.header`
        falls back to the model field's `verbose_name` -- so a fix on one side does not imply the
        other. `created`/`last_updated` were frozen here on every table in the product while the
        form side was already correct.
        """
        import importlib
        import pkgutil

        from django.utils.functional import Promise
        import django_tables2 as django_tables

        import nautobot as nautobot_package

        catalog = self._translated_msgids()
        self.assertNotEqual(catalog, set(), "no translated msgids found; this check would pass vacuously")

        modules = []
        for info in pkgutil.walk_packages(nautobot_package.__path__, prefix="nautobot."):
            name = info.name
            if ".tests" in name or ".migrations" in name or "test_jobs" in name or not name.endswith(".tables"):
                continue
            with contextlib.suppress(Exception):
                modules.append(importlib.import_module(name))

        frozen, seen = [], set()
        for module in modules:
            for attr in dir(module):
                obj = getattr(module, attr, None)
                if not isinstance(obj, type) or not issubclass(obj, django_tables.Table):
                    continue
                key = f"{obj.__module__}.{obj.__name__}"
                if key in seen or obj.__module__.startswith(("django", "django_tables2")):
                    continue
                seen.add(key)
                for column_name, column in getattr(obj, "base_columns", {}).items():
                    # Columns contributed by an App belong to that App's own catalog.
                    if column_name.startswith("cf_") or "example_app" in column_name:
                        continue
                    verbose = column.verbose_name
                    if verbose is None or isinstance(verbose, Promise) or not isinstance(verbose, str):
                        continue
                    plain = " ".join(verbose.split())
                    if plain in catalog and plain not in self.KNOWN_EXCEPTIONS:
                        frozen.append(f"{key}.{column_name}: {plain!r}")

        self.assertEqual(
            sorted(set(frozen)),
            [],
            "these column headers have a translation in the catalog but are stored as plain `str`, "
            "so the header renders in one fixed language. Mark the underlying model field's "
            "`verbose_name`:\n" + "\n".join(sorted(set(frozen))),
        )


class FilterLabelTestCase(TestCase):
    """Lookup-expression filter labels are composed per request, and must stay that way."""

    def test_lookup_expression_filter_labels_are_translated(self):
        """
        `comments__ic` and its thousands of siblings translate without any catalog entry of ours.

        `label_for_filter()` composes the label at filterset instantiation from the model field's
        `gettext_lazy` `verbose_name` plus a lookup verb from django-filter's own catalog. This test
        exists because the arrangement is easy to break in two ways: marking a field's
        `verbose_name` as a plain string, or "fixing" these filters by giving them an explicit
        `label=`, which replaces a computed label with a frozen one.
        """
        from nautobot.circuits.filters import ProviderNetworkFilterSet

        rendered = {}
        for language in ("en", "de", "fr"):
            with translation.override(language):
                rendered[language] = str(ProviderNetworkFilterSet().filters["comments__ic"].label)

        self.assertEqual(rendered["en"], "Comments contains")
        self.assertNotEqual(
            rendered["de"],
            rendered["en"],
            "lookup-expression filter labels are no longer translated; check that the model field's "
            "`verbose_name` is still a lazy proxy and that no explicit `label=` was added",
        )
        self.assertNotEqual(rendered["fr"], rendered["en"])
