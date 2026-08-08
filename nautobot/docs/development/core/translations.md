# Translations

+++ 3.2.0

Nautobot uses [Django's standard i18n framework](https://docs.djangoproject.com/en/stable/topics/i18n/).
This page is for core contributors: how to mark a string translatable, and what to do when you
change one.

For the administrator-facing view — which languages are offered, how users select one, and what is
deliberately never translated — see the
[Internationalization guide](../../user-guide/administration/guides/internationalization.md).

## If you change a translatable string

Run:

```no-highlight
invoke makemessages
```

and commit the resulting `nautobot/locale/**/*.po` changes with your code change.
`invoke check-translations` runs as part of `invoke lint` and will fail if the catalogs are stale.

!!! tip "A one-word edit costs five translations"
    Editing an existing string invalidates its translation in every language. Reword only when the
    current wording is actually wrong or unclear, not for taste.

## Marking strings translatable

### Python

Use `gettext_lazy` (conventionally aliased `_`) for anything evaluated at import time — model
fields, form fields, table columns, choice labels, UI component labels:

```python
from django.utils.translation import gettext_lazy as _

class Device(PrimaryModel):
    name = models.CharField(
        max_length=CHARFIELD_MAX_LENGTH,
        verbose_name=_("Name"),
        help_text=_("The name of this device"),
    )
```

Use plain `gettext` only inside a function that runs per request, where the active language is
already established.

### Flash messages

Messages must use `gettext`, **never** `gettext_lazy`:

```python
from django.utils.translation import gettext

messages.success(request, gettext("Your preferences have been updated."))
messages.warning(request, gettext("No %(object_name)s were selected.") % {"object_name": name})
```

A message is stored and rendered on the *next* request, and the cookie-backed message store
JSON-encodes it — a lazy proxy raises there. Immediate evaluation is correct because the redirect
target is the same user in the same language.

!!! warning "f-strings cannot be extracted"
    `xgettext` cannot see inside an f-string, so `f"No {name} were selected."` is invisible to the
    translation pipeline no matter how visible it is in the UI. Use a `%`-format placeholder:

    ```python
    # Wrong -- never extracted
    messages.warning(request, f"No {name} were selected.")

    # Right
    messages.warning(request, gettext("No %(object_name)s were selected.") % {"object_name": name})
    ```

    Name placeholders for what they mean (`%(count)s`, not `%(selected_objects)s`) — the translator
    sees only the name, and may need to move it within the sentence.

### Templates

```jinja
{% load i18n %}

<button>{% trans "Cancel" %}</button>
```

When a sentence contains a variable or inline markup, use `{% blocktrans %}` so the translator sees
a whole sentence:

```jinja
{% blocktrans trimmed %}
    Required fields <strong>must</strong> be present in the data.
{% endblocktrans %}
```

!!! warning "Never build a sentence out of separately translated fragments"
    `{% trans "Required fields" %} <strong>{% trans "must" %}</strong> {% trans "be present." %}`
    gives a translator three meaningless fragments and forces English word order on every language.
    Use one `blocktrans` instead.

### JavaScript

Import from the i18n shim in `nautobot/ui/src/js/i18n.js`:

```javascript
import { gettext, interpolate } from './i18n.js';

button.textContent = gettext('Collapse All Groups');
badge.textContent = interpolate(gettext('in: %(name)s'), { name });
```

Interpolate with named placeholders rather than concatenating: the position of an inserted value
within a sentence differs between languages.

## What not to mark

Read the [scope boundary](../../user-guide/administration/guides/internationalization.md#what-gets-translated-and-what-never-does)
before wrapping anything. The short version:

- **Never** wrap a ChoiceSet *value*. Only the label. The value is an API contract.
- **Never** wrap protocol or standard identifiers (`VLAN`, `RJ-45`, `AES-128-GCM`, `1 Gbps`), or
  product and vendor names. Several ChoiceSets are deliberately left entirely untranslated for this
  reason.
- **Never** wrap text destined for the database — job log messages, change-log snapshots.
- **Never** wrap a Job's `Meta.name`, `description` or `grouping`. `Job._get_meta_attr_and_assert_type()`
  requires a real `str` and rejects a lazy proxy, and the value is copied into the `Job` database
  record at registration — a translated one would freeze whichever language was active during
  `post_upgrade`.

Before wrapping anything that is not obviously a label, ask what reads it downstream. A string is
safe only if nothing **stores** it, **compares** it, or **publishes** it as a contract. Rendering
correctly in German is not sufficient evidence — the optgroup headings in grouped `ChoiceSet`s
render fine and were still reverted, because drf-spectacular turns them into API filter enum values.
The cheap check is to generate the API schema under two languages and confirm only
`.../properties/label` entries differ:

```python
from django.utils import translation
from drf_spectacular.generators import SchemaGenerator

for language in ("en", "de"):
    with translation.override(language):
        schema = SchemaGenerator().get_schema(request=None, public=True)
```

## Filter labels translate themselves

Lookup-expression filters -- `comments__ic`, `name__nisw`, and the several thousand others Nautobot
generates -- carry no `label` of their own. `django_filters.utils.label_for_filter()` composes one at
**filterset instantiation**, from two already-translatable pieces:

- the model field's `verbose_name`, which is a `gettext_lazy` proxy, and
- the lookup verb, which django-filter ships translated in its own catalog.

So `comments__ic` renders `Comments contains` / `Kommentare enthält` / `Commentaires contient` with no
entry in `nautobot/locale/`. Nothing needs marking, and adding explicit `label=` arguments would
*remove* that behaviour by replacing a computed label with a fixed one.

!!! warning "Do not measure these by reading `.label`"
    `FilterSet.base_filters[name].label` is `None`, and `FilterSet().filters[name].label` is a plain
    `str` computed under whichever language was active when you instantiated it. Both look like
    untranslatable text to a naive audit. Instantiate the filterset inside `translation.override()`
    and compare across two languages instead.

Filters that *do* declare a label -- `label=_("Contacts (name or ID)")` and similar -- are ordinary
marked strings and need catalog entries like anything else.

## Hazards worth knowing

**Lazy objects are not strings.** `gettext_lazy` returns a promise that resolves when it is
rendered. That is what makes per-request language selection work, but it means:

- `json.dumps` from the standard library raises on a lazy value. `DjangoJSONEncoder` coerces lazy
  *values*, but a lazy dict *key* still raises. Call `str()` at serialization boundaries.
- A lazy value used as a dict key, or compared for identity, will not behave as you expect.
- Anything cached must be keyed by language, or one user's language leaks to another.

**A `{% trans %}` inside a Python string is invisible to `makemessages`.** `makemessages` runs the
Python extractor over `.py` files -- it looks for `gettext()` calls, not template syntax -- and the
template extractor only over `.html`. A template fragment held in a Python literal, which is how
`django-tables2` column markup is conventionally written, falls between them. Nothing appears to be
wrong: gettext falls back to the msgid, so the fragment renders in English and keeps rendering in
English in every language, with no catalog entry a translator could fill in.

Declare the msgids beside the fragment so the Python extractor sees them:

```python
IPADDRESS_OR_RANGE_ACTIONS = """\
{% load i18n %}
...
<span class="mdi mdi-pencil me-4" aria-hidden="true"></span>{% trans "Edit IP address" %}
"""

TRANSLATABLE_IPADDRESS_OR_RANGE_ACTIONS = (
    gettext_noop("Edit IP address"),
)
```

Such a fragment also needs its own `{% load i18n %}`: django-tables2 renders it standalone, so a
`{% load %}` in the surrounding page does not apply. `EmbeddedTemplateStringTestCase` fails on any
`{% trans %}` in a `.py` file whose msgid is missing from the catalog.

**Registry keys must stay English.** The navigation registry is keyed by `name`, which is why
`NavMenuTab`/`NavMenuGroup`/`NavMenuItem` have a separate `label`. See
[Navigation Menu](navigation-menu.md).

**Model metadata is migration-invisible.** Wrapping `verbose_name` or `help_text` in `gettext_lazy`
does not generate a migration, because a lazy string compares equal to its resolved value. Run
`invoke check-migrations` if you are unsure.

## Apps

Apps ship their own catalogs; Django discovers a `locale/` directory in any installed app, so an
App's strings are translated by the App and not from `nautobot/locale/`. See
[Shipping Translations from an App](../apps/api/translations.md) for the App-side contract, and
`examples/example_app/` for a worked example.

Two consequences for core work:

- `invoke makemessages` ignores `examples/*`. Django treats any directory named `locale` as an
  additional output path, so without that the example Apps' strings would be hoisted into Nautobot's
  catalogs and core would end up translating them.
- Core wins a msgid an App also defines. `LOCALE_PATHS` is merged after the installed-app catalogs,
  so an App cannot override a core translation by translating the same English string.

## Invoke tasks

| Task | Purpose |
| ---- | ------- |
| `invoke makemessages` | Re-extract translatable strings into the `.po` catalogs |
| `invoke compilemessages` | Compile `.po` to the `.mo` files Django reads at runtime |
| `invoke check-translations` | Validate catalogs and fail if they are out of date. Included in `invoke lint` |

These require the GNU gettext tools (`xgettext`, `msgfmt`). They are installed in the development
container; on a local install use your platform's `gettext` package.

## Strings you do not have to translate

`gettext` searches the merged catalogs — Nautobot's, every installed app's, and Django's own — so a
message left empty in `nautobot/locale/` can still reach the user in their language if another
catalog supplies it. Django and Django REST Framework ship translations for the languages Nautobot
ships, and those are verified to reach the UI: form validation errors ("This field is required."),
admin chrome, and DRF API errors all render translated without any entry of ours.

About 40 messages per catalog are in that category. They are almost all Django admin strings, picked
up because Nautobot overrides some admin templates and extraction cannot tell an overridden template
from an original. Leaving them empty is correct — filling them in duplicates work Django has already
done, and risks drifting from Django's own wording.

To list them for a given language:

```python
# nautobot-server shell
from django.utils import translation
from django.utils.translation import gettext
with translation.override("de"):
    print(gettext("Django site admin"))  # -> 'Django-Systemverwaltung', with no entry of ours
```

This also means the raw translated/total ratio understates what an operator actually sees, though
only slightly — about one percentage point.

## Translation quality and governance

The catalogs currently in the repository are **machine-assisted and pending native-speaker review**,
recorded in each catalog's `X-Translation-Source` header. Before any language is presented as
generally available it needs a named native-speaker reviewer.

Translation content is a supply-chain surface: a malicious or careless translation can inject
misleading text, and mismatched format placeholders between `msgid` and `msgstr` are both a crash
vector and the classic injection vector. `invoke check-translations` runs `msgfmt --check`, which
catches placeholder mismatches. Catalog changes should be reviewed like code.
