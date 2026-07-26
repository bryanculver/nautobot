# Shipping Translations from an App

An App can ship its own translation catalogs. Nothing has to be registered with Nautobot: there is no
setting, no `NautobotAppConfig` attribute, and nothing to add to `LOCALE_PATHS`.

Django discovers a `locale/` directory inside every entry in `INSTALLED_APPS`, and Nautobot appends
each `PLUGINS` entry to `INSTALLED_APPS` at startup. Ship the directory inside your package and your
strings are translated alongside Nautobot's.

`examples/example_app/` in the Nautobot repository is a working example of everything below.

## Directory layout

Put the catalogs *inside the Python package*, beside `models.py` — not at the repository root:

```no-highlight
my_app/
├── my_app/
│   ├── __init__.py
│   ├── locale/
│   │   └── de/
│   │       └── LC_MESSAGES/
│   │           ├── django.po
│   │           └── django.mo
│   ├── models.py
│   └── navigation.py
└── pyproject.toml
```

Directory names are *locale* names, not language codes: `zh_Hans` and `pt_BR`, where the `LANGUAGES`
setting spells the same languages `zh-hans` and `pt-br`.

## Marking strings

Exactly as in Nautobot core — see [the core guide](../../core/translations.md) for the full
conventions, including what not to mark.

```python
from django.utils.translation import gettext_lazy as _

from nautobot.apps.ui import NavMenuItem

NavMenuItem(
    link="plugins:my_app:widget_list",
    name="Widgets",            # stable key: other Apps attach to it, tests select on it
    label=_("Widgets"),        # display text: this is what gets translated
    permissions=["my_app.view_widget"],
)
```

+++ 2.4.0
    `NavMenuTab`, `NavMenuGroup` and `NavMenuItem` accept a `label` separate from `name`. `label`
    defaults to `name`, so adding one is optional and changes nothing until you do.

Use `gettext_lazy` rather than `gettext` for anything evaluated at import — menu items, model fields,
form fields, choice labels. A `gettext` call at import time resolves once, in whatever language was
active during startup, and serves that to every user forever.

## Building the catalogs

Run these **inside your package directory**, so that Django writes to your `locale/` and not
somewhere else:

```no-highlight
cd my_app/my_app
mkdir -p locale
django-admin makemessages --locale de --no-wrap
django-admin makemessages --locale de --no-wrap --domain djangojs   # only if you ship JavaScript
django-admin compilemessages
```

!!! warning "Create `locale/` first"
    If the directory does not exist, `makemessages` falls back to the first entry of
    `settings.LOCALE_PATHS` — which, under Nautobot settings, is Nautobot's own catalog directory.
    Your App's strings would be written into Nautobot's catalogs.

!!! tip "`django-admin`, not `nautobot-server`"
    `nautobot-server` loads Nautobot's settings, so `compilemessages` would also recompile
    Nautobot's own `.mo` files and dirty your checkout. `django-admin` with no
    `DJANGO_SETTINGS_MODULE` touches only the `locale/` tree beneath the current directory.

`--no-wrap` keeps one message per line, which makes catalog diffs reviewable.

## Packaging the compiled catalogs

**Django reads `.mo` and never `.po`.** A distribution containing only `.po` files has no
translations at all — and it installs perfectly cleanly, so nothing tells you.

This bites because the standard GitHub Python `.gitignore` lists `*.mo`, and poetry, hatchling and
setuptools all skip VCS-ignored files when building. Declare them explicitly:

=== "Poetry"

    ```toml
    [tool.poetry]
    include = [
        {path = "my_app/locale/**/*.mo", format = ["sdist", "wheel"]},
    ]
    ```

=== "setuptools"

    ```toml
    [tool.setuptools.package-data]
    my_app = ["locale/*/LC_MESSAGES/*.mo"]
    ```

=== "Hatch"

    ```toml
    [tool.hatch.build]
    artifacts = ["my_app/locale/**/*.mo"]
    ```

Verify the built artifact rather than trusting the configuration:

```no-highlight
python -m zipfile -l dist/*.whl | grep '\.mo'
```

## Testing your catalogs

`nautobot.apps.testing` provides the same integrity checks Nautobot runs against its own catalogs:

```python
from pathlib import Path

from nautobot.apps.testing import TestCase, TranslationCatalogTestCaseMixin


class MyAppTranslationTestCase(TranslationCatalogTestCaseMixin, TestCase):
    locale_path = Path(__file__).resolve().parent.parent / "locale"
```

That asserts every `.po` has a compiled `.mo` beside it, that each `.mo` is the current compilation
of its source, and that plural entries carry exactly as many forms as the catalog declares.

## Constraints

**Nautobot core wins a msgid you both define.** Django merges installed-app catalogs first and
`LOCALE_PATHS` — Nautobot's own — last, and the later merge takes precedence. You cannot override a
core translation by translating the same English string. In practice this is usually what you want:
reuse a core string and you inherit its translation for free.

**A language must be in `LANGUAGES` before anyone can select it.** `UserDefinedLanguageMiddleware`
only activates languages present in that setting. Shipping a `ja` catalog does nothing until the
operator adds `("ja", "日本語")` to `LANGUAGES` — so document that in your App's install
instructions; it is not something the App can do for itself.

**Locale-aware date and number formats cover only the languages Nautobot ships.**
`FORMAT_MODULE_PATH` has modules for `de`, `en`, `es`, `fr` and `zh_Hans`. For any other language
Django falls back to its own formats, and an operator's `DATE_FORMAT` overrides stop applying.

**Get your `Plural-Forms` header right.** A merged catalog takes its plural rule from the first
catalog merged, so an incorrect header in an App catalog can affect pluralization beyond your own
strings.

## Why there is no configuration for this

Discovery happens inside Django, in `django.utils.translation`, from `INSTALLED_APPS` and the
filesystem. Nautobot cannot influence it from a config attribute without reimplementing Django's
translation loading. An attribute such as `locale_dir` or `translations = True` would either agree
with the filesystem (redundant) or disagree with it (misleading — translations would keep working
after you set it to `False`). Convention is the whole mechanism.
