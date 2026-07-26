# Internationalization

+++ 3.2.0

Nautobot can present its user interface in languages other than English. This page covers what is
translated, how users select a language, and what an administrator needs to know before enabling it.

## Status: beta

!!! warning "Translations are machine-assisted and pending native-speaker review"
    The translations shipped in this release were produced with machine assistance and have **not**
    yet been reviewed by native speakers. Each catalog records this in its `X-Translation-Source`
    header. Treat non-English languages as a beta feature: usable and useful, but expect wording
    that a native speaker would improve.

    If you would like to help review or improve a language, see
    [issue #5224](https://github.com/nautobot/nautobot/issues/5224).

Translation coverage is also **partial**. The everyday interface chrome — navigation, buttons,
common field labels, table headings, and status vocabulary — is translated. Longer help text and
less-common forms are not yet, and are shown in English.

This is normal and expected: gettext falls back to the original English string whenever a
translation is missing, so an untranslated string is never broken, only untranslated. A
partially-translated product is how essentially every large open-source project ships.

## What gets translated, and what never does

The dividing line is where the text came from:

> **Did this text come out of Nautobot's source code, or out of a database row?**
> Source code translates. Database rows and anything a user typed never do.

**Translated:** navigation labels, buttons, page titles, form and filter labels, field help text,
model names, table column headings, and the display labels of choice fields.

Never translated:

- **Your data.** Device names, location names, descriptions, and custom field *values* are yours.
  Translating them would corrupt your data and break automation that matches on them.
- **Editable database rows** such as Status and Role names. These are records you can rename, not
  strings in our source code. A catalog translation would silently diverge from your database the
  first time anyone edited a row.
- **Protocol and industry terms** — VLAN, BGP, VRF, IPv6, rack unit "U", vendor names. These are
  the industry's shared vocabulary; translating them makes the interface *harder* to read, not
  easier. They stay verbatim even inside an otherwise translated sentence.
- **Machine contracts** — REST API field names, GraphQL schema names, keys and slugs, choice field
  *values*, and webhook payload keys. These are wire format. The label "Planned" may appear in your
  language; the underlying value `planned` never changes.
- **Records of fact** — job log entries and change-log snapshots are written once, in the language
  that was active when the event happened, like syslog. Retroactively translating them would
  falsify history.

## Selecting a language

Language is chosen **per user**, and applies only to that user's own sessions, from
`User → Preferences → Language`.

Users who never make a selection continue to see the language given by
[`LANGUAGE_CODE`](https://docs.djangoproject.com/en/stable/ref/settings/#language-code), which is
English. Selecting the blank option returns a user to that default.

!!! info "Nautobot does not auto-detect language"
    Nautobot deliberately ignores the browser's `Accept-Language` header. Automatic detection would
    change the interface language for existing users the moment they upgraded, without anyone
    asking for it. Language is always an explicit, per-user opt-in.

!!! warning "Pages shown before login are always in the default language"
    Because the language comes from the signed-in user's preference, there is no user to read it
    from on the login page, the logout confirmation, or an error page served to an anonymous
    visitor. Those always render in [`LANGUAGE_CODE`](https://docs.djangoproject.com/en/stable/ref/settings/#language-code).

    This is a direct consequence of not negotiating on `Accept-Language`, and it is a deliberate
    trade: the alternative would change the language for existing users without being asked. If
    your deployment needs a translated login page, set `LANGUAGE_CODE` to that language — it
    becomes the default for everyone who has not chosen otherwise.

## Configuring which languages are offered

The [`LANGUAGES`](../configuration/settings.md#languages) setting controls what users can choose
from. It defaults to every language Nautobot ships:

```python
LANGUAGES = [
    ("en", "English"),
    ("de", "Deutsch"),
    ("es", "Español"),
    ("fr", "Français"),
    ("zh-hans", "中文（简体）"),
]
```

To offer only a subset, narrow the list. To turn the feature off entirely, reduce it to English:

```python
LANGUAGES = [("en", "English")]
```

A user whose stored preference is no longer in `LANGUAGES` falls back to the default language
rather than erroring.

## Date and time formats

Date and time rendering follows the user's language — a French user sees `23 février 2026` — unless
you have explicitly configured a format yourself.

The precedence rule is:

1. If you set [`DATE_FORMAT`](../configuration/settings.md#date_format),
   [`DATETIME_FORMAT`](../configuration/settings.md#datetime_format),
   [`SHORT_DATE_FORMAT`](../configuration/settings.md#short_date_format),
   [`SHORT_DATETIME_FORMAT`](../configuration/settings.md#short_datetime_format), or
   [`TIME_FORMAT`](../configuration/settings.md#time_format) to a non-default value, **that format
   is used in every language.** Organizations that mandate ISO dates do so deliberately, and
   Nautobot will not silently ignore that for non-English users.
2. If you leave a format at its default, non-English languages use that language's own conventions.

!!! note
    Nautobot detects "the administrator configured this" by comparing against the shipped default.
    Setting a format to *exactly* the default value is therefore indistinguishable from not setting
    it, and non-English languages will use their own conventions in that case.

## Caveats for administrators

**If you override `MIDDLEWARE` wholesale** in `nautobot_config.py`, you must include
`nautobot.core.middleware.UserDefinedLanguageMiddleware` yourself, or language selection will have
no effect. Most deployments do not override `MIDDLEWARE` and need do nothing.

**Whether an App is translated is up to that App.** Apps may ship their own translation catalogs,
and Nautobot serves them automatically. An App that does not is unaffected and keeps working -- its
pages simply render in English -- so expect a mixed-language interface if you run Apps that have not
adopted translations yet. If an App ships a language Nautobot does not list, add it to `LANGUAGES`
before users can select it.

**The GraphQL browser (GraphiQL) is permanently English.** It has no internationalization support
upstream.

**Fonts.** Nautobot ships Latin, Greek, and Cyrillic fonts. Chinese text falls back to whatever
your operating system provides, which renders correctly but may not match the surrounding
typography exactly.

**REST API schema output** is generated in whatever language is active at generation time. If you
cache schema output, key that cache by language or pin generation to English.

## For app developers

Apps require **no changes** and will continue to work exactly as they do today.

If you want your app's navigation entries to be translatable ahead of the full app contract, the
`NavMenuTab`, `NavMenuGroup`, and `NavMenuItem` classes accept an optional `label` argument:

```python
from django.utils.translation import gettext_lazy as _

NavMenuItem(
    link="my_app:widget_list",
    name="Widgets",          # Stable key: never translate this
    label=_("Widgets"),      # Display text: translated per request
)
```

`name` remains the stable identifier. It is how apps attach groups to existing tabs, what user
"favorites" are stored against, and what integration tests select on — so it must not change with
the active language. `label` defaults to `name`, which is why apps that pass only `name` are
unaffected.
