# Nautobot i18n MLP — Session Report

**Branch:** `u/bryanculver-i18n-pilot` (9 commits off `develop`, one per review layer)
**Scope:** the MLP described in `i18n-research/02-implementation-plan.md` (WB1–WB11)
**`git push` was never invoked.**

Read this before the diff. It records what shipped, what deliberately did not, the outcomes of the
two checkpoints the plan called for, and the four places where I departed from the plan on purpose.

---

## 1. What shipped

The branch is organised as nine review layers rather than one commit per work item. Layers 1–5
carry every design decision; layers 6 and 7 are the bulk mechanical `"Text"` → `_("Text")` change,
which is why they come last and can be skimmed for pattern conformance rather than read for intent.

| Layer | Substance | Work items |
| --- | --- | --- |
| 1 | Language selection, `UserDefinedLanguageMiddleware`, D-1 format precedence, `<html lang>` | WB1–WB4 |
| 2 | Nav/homepage `name` (key) vs `label` (display), lazy-safety in the UI framework | WB5, WB6 |
| 3 | Unicode and identifier correctness | WB10 |
| 4 | Invoke tasks, JS catalog, packaging, catalog-integrity tests | WB7 |
| 5 | Operator, app-developer and contributor documentation | WB11 |
| 6 | Mark translatable strings in Python (~250 files) | WB8a/b, WB12 |
| 7 | Mark translatable strings in templates (~285 files) | WB8c |
| 8 | de/es/fr/zh_Hans catalogs (generated) | WB9 |
| 9 | Example App adopts its own catalogs — the App-side migration path, end to end | — |

Every layer passes `nautobot-server check` on its own. The *test suite* is a different matter:
`nautobot/core/tests/test_translations.py` arrives in layer 4 but the catalogs it inspects arrive in
layer 8, so those tests are red at layers 4-7 by construction — there is no `nautobot/locale/`
directory to read yet. That is a consequence of putting the generated catalogs last, which is what
makes layers 6 and 7 skimmable; the alternative (catalogs first) would have made the mechanical
marking layers unreadable. Run the suite at layer 8 or at the branch head.

Every layer passes `nautobot-server check` on its own, so the branch can be bisected.

**Extraction:** 3660 unique translatable strings.
**Translation:** 1807 per language (~49%), covering the everyday chrome. Roughly 40 further
messages per catalog are supplied by Django's own catalogs and are intentionally left empty; see
the contributor guide.

---

## 2. Checkpoint outcomes

**WB8 migration checkpoint — PASSED, model wrapping stayed in scope.**
The plan made model-layer wrapping conditional on `invoke check-migrations` staying clean, with the
fallback of dropping it entirely. `Promise.__eq__` resolves to string equality, so the autodetector
sees no change. Verified twice: after the dcim pilot, and again after all 575 sites. Both reported
"No changes detected".

**Schema checkpoint — PASSED.** `invoke check-schema` is clean across all seven API versions.
drf-spectacular's `normalize_result_object` coerces `Promise` to `str` on every generated schema.
*Operational consequence:* schema output is now locale-dependent at generation time. Any schema
caching must be locale-keyed or pinned to English. Documented.

---

## 3. Deliberate departures from the plan

These are the decisions a reviewer should look at hardest.

### 3.1 CSV export BOM is opt-in, not unconditional (G-10)

The plan called for adding a UTF-8 BOM to REST API CSV export for parity with the UI path.
Implementing that unconditionally **broke Nautobot's own round-trip test**, which is a realistic API
client: a BOM corrupts the first header for anything decoding plain `utf-8`.

API CSV is consumed programmatically far more often than it is opened in Excel, so an unconditional
BOM trades a Medium-severity convenience win for a breaking change to every existing consumer. It is
now `?bom=true`. The import-side fix (G-11, the actual data-loss bug) is unconditional.

**This is a product call, not an engineering one — flagging it for an explicit decision.**

### 3.2 34 ChoiceSets deliberately left untranslated

Blanket-wrapping all ~650 choice labels would have put `mdi-plus-thick`, `IEC 60320 C14`,
`AES-128-GCM`, and `1 Gbps` into the translation catalog. Per the platform glossary these are
industry lingua franca where translation *reduces* comprehension.

342 product-vocabulary labels (statuses, actions, types) are wrapped; 34 identifier ChoiceSets are
not. The exclusion list is explicit in the commit and reviewable per entry — moving one either way
is a one-line change. **Worth a reviewer's eye:** `RadioProfileRegulatoryDomainChoices` (country
names paired with ISO codes) and `ButtonColorChoices` are the two genuinely arguable calls.

### 3.3 `theme_preview.html` not extracted

It is a developer style gallery whose text is icon names (`arrow-decision icon`), Bootstrap demo
filler (`@fat`, `@mdo`, "Best check yo self"), and swatch labels. Extracting it added ~250 junk
msgids. Excluded.

### 3.4 Language preference is clearable

The reverted #8417 had no way back: `if language := form.cleaned_data["language"]` meant selecting
blank did nothing. Timezone has the same one-way behavior, but timezone does not change the language
of the control you need to fix it with. A user who switches to a language they cannot read must be
able to undo it, so the blank choice now clears the preference.

---

## 4. Departures the plan anticipated, resolved as specified

- **D-1** resolved as option (c): an explicitly configured operator format wins in every language;
  otherwise per-language defaults. Verified live in all five languages.
- **No `Accept-Language` negotiation.** Stock `LocaleMiddleware` is deliberately not used.
- **Zero app changes.** Verified: all 5 Example App nav entries have `label == name` and render in
  English inside a German UI.

---

## 5. Bugs found and fixed that were not in the plan

The template codemod produced real breakage before being made safe. Each of these was caught by
`nautobot-server validate_templates`, which reports the same 3 pre-existing failures before and
after this branch and no new ones:

1. `{% if a > 1 and not b %}` is indistinguishable from an HTML text node — it sits between a `>`
   and a `<`. Rewriting it produced an unparseable template.
2. `{% include ... with title="x" %}` is indistinguishable from an HTML attribute.
3. `{# ... #}` comments were being rewritten.
4. Nautobot's heavy use of the `<!-- -->` whitespace-control idiom put 57 real UI strings at a chunk
   boundary where a naive text-node match could not see them.

Also fixed incidentally: three `_` loop variables and unpacking targets that shadowed the `gettext`
alias (`dcim/models/locations.py`, `core/tables.py` ×2).

### Plural forms were silently untranslated, and Chinese was structurally wrong

Found by checking something no earlier pass had: every sweep in this session diffed English against
**German only**. Spanish, French and Chinese were never verified end to end.

Two defects surfaced:

- **`msgstr[n]` entries were never written.** The script that populates the catalogs only understood
  the singular `msgstr ""` form, so every `{% blocktrans count %}` message stayed untranslated in
  all four languages regardless of how many times it was regenerated.
- **Chinese declared `nplurals=1` but carried two plural forms.** `msgfmt --check` does not flag
  this while the entries are empty, so it would only have failed once someone translated them --
  a trap laid for the next person, not a visible error.

Both fixed, and one `blocktrans count` block was simplified to a plain `blocktrans` because its
singular and plural text were identical, which makes the plural machinery pointless.

All four languages are now verified rendering live: 160-230 strings change per page in each.

### Two defects found by a post-implementation audit

Neither was in the plan; both were found by writing assertions over the finished diff rather than
by reading it.

**The cached OpenAPI schema varied by user language.** `NautobotSpectacularAPIView` caches the
generated schema for seven days under a key with no language component, and serves it with
`Cache-Control: public`. Once model metadata became translatable, whichever user warmed that cache
decided the language served to everyone else. Schema generation is now pinned to `LANGUAGE_CODE`.
This is the R6 hazard from the gap analysis landing exactly where it was predicted to.

**One navigation group was silently left untranslated.** The WB5 codemod matched `name="...",` at
end of line, so `NavMenuGroup(name="Metadata",  # TODO: ...)` — the one entry carrying a trailing
comment — was skipped. Found by asserting that every `NavMenu*` call with a `name=` also has a
`label=`.

Two audits now back these up and are worth re-running after any future extraction work:

- every `NavMenu*` `name=` is a plain string and every `label=` is lazy (183/183 clean);
- no ChoiceSet *value* is wrapped in `gettext`, across all 1150 choice pairs — the API contract is
  intact by assertion, not by inspection.

### English-specific string transforms applied to translated text

A recurring class, worth knowing about because the next person to add a transform will hit it. Each
was invisible in English and only wrong once the input was translated:

- **Derived plurals.** Django builds an unset `verbose_name_plural` as `verbose_name + "s"`.
  Detailed in §6 — it is a constraint on the pending migration decision, not just a past bug.
- **`bettertitle`.** Capitalised every word, which is English title case. French and Spanish
  capitalise only the first word; German capitalises nouns, not adjectives. It produced
  "Políticas VPN De Fase 1" and "Affectations D'adresses IP". Now language-aware.
- **Django's `title` filter**, applied to object type names, was the same bug plus lower-casing the
  rest of each word ("IP address" → "Ip Address"). Replaced with `bettertitle`.
- **`|pluralize`** appended an English "s" to counts of interfaces and cable peers. Replaced with
  `{% blocktrans count %}`, which lets each catalog choose its own number of plural forms.

Checked and found *not* to be instances of the class: `|slugify` on panel and search identifiers
(they derive from stable keys, not display text), `|first|upper` on nav letter icons, and CSS
`text-transform: uppercase` — the last is correct precisely because layer 1 sets `<html lang>`, so
browsers apply locale-aware casing.

### A defect in the translation tooling itself

`invoke makemessages` clears the translations `msgmerge` guesses, because a wrong guess that gettext
ignores is worse than an honest blank. That clearing matched `msgstr "..."` only — so for
*pluralised* entries it stripped the `fuzzy` marker while leaving the guess in place, promoting an
ignored guess into a translation gettext actually serves. Three of the five plural entries in every
catalog were affected; German showed "Übergeordnetes Interface" ("parent interface") for
`%(count)s interface`. Fixed, and two tests now guard the shapes the clearing code assumes: every
plural entry carries exactly the number of forms its catalog declares, and no translation is wrapped
across continuation lines.

### Filter labels were frozen in the first reader's language

`nautobot/core/filters.py` composed filter labels with `force_str` over parts that are lazy and
translated — the model field's `verbose_name` and django-filter's lookup vocabulary — then stored
the result. One builder runs at class construction, so those labels were permanently English. The
other cached onto a filter that lives on the filterset *class*, so **whichever language first
touched a label fixed it for every later request, for every user**. That is a cross-request leak,
not only a missing translation.

Both now compose lazily, and 2760 filter labels translate as a result ("Has cable" → "Hat Kabel").
The `exclude` prefix is translated as a preposition — "ohne", "sin", "sans" — because it is
prepended to a field label and a verb reads wrongly there.

---

## 6. Known gaps — recommended follow-up issues

### Blocked on a decision

**Only model *names* are gated. Field labels are not — this corrects an earlier claim in this
report.** Django 4.1 introduced `Field.non_db_attrs`, which in Django 5.2 contains `verbose_name`
and `help_text` among others. Changing or adding either **on a model field generates no migration**.
Verified two ways: `Field.non_db_attrs` inspected directly, and empirically by adding
`verbose_name=_("Contact name")` to `dcim.Location.contact_name`, after which
`makemigrations --check` reported "No changes detected" — with a control change to `max_length` on
the same model confirming the detector was working.

`Meta.verbose_name` / `verbose_name_plural` are model *options*, not field attributes, and those do
still generate `AlterModelOptions`. So the gate is narrower than described below: it covers the
model *name* shown in page titles and buttons, but **not** the form labels and table column headers
that come from field `verbose_name`. Those — "Contact name", "Facility", "Amperage", "Breaker
position", "Cable type" — are the most visible remaining English on list and detail pages, and they
can be translated today with no migration at all. 2453 model fields currently fall back to a derived
English name; the user-visible subset (concrete fields, excluding reverse relations and internal
fields like `_custom_field_data`) is the tranche worth doing, and it is now the highest-value
unblocked work on this branch.

**Translatable model names require migrations.** **157 of Nautobot's 165 models render an English
name under a non-English UI** — measured by rendering `verbose_name_plural` under `de` and
comparing, which is a stricter test than counting models without an explicit `Meta.verbose_name`
(the earlier figure of 132 missed models whose explicit `verbose_name` was never wrapped). That
single gap is why "device", "circuit type", "cluster" and so on stay English inside otherwise
translated page titles, table headers, buttons, breadcrumbs, and empty states. It is the largest
remaining source of visible English.

Fixing it means adding `verbose_name = _("...")` / `verbose_name_plural = _("...")` to each model's
`Meta`. **Verified empirically:** doing so generates an `AlterModelOptions` migration per model.
Those are state-only operations -- no SQL, no data change, no downtime -- but 157 of them across 13
apps is a large, conflict-prone diff, and WB8's checkpoint was explicitly about not generating
migrations.

**Whoever does this must set `verbose_name_plural` alongside `verbose_name`, never alone.** Django
derives an unset plural as `verbose_name + "s"`, so translating only the singular appends a Latin
"s" to translated text -- German "Gruppe" became "Gruppes" rather than "Gruppen", and Chinese "组"
became "组s". Three models shipped that defect before it was caught; a further 16 are latent, fine
only because their singular is not translated yet. `test_translated_verbose_name_requires_explicit_plural`
now fails the moment a model translates its singular without declaring a plural, so the trap is
guarded rather than merely documented.

Two related fixes are already in place ahead of this decision, and both matter once 157 model names
start translating: `bettertitle` no longer applies English title case to translated text, and the
places that used Django's `title` filter on object type names now use `bettertitle` instead.

This needs a maintainer decision rather than an implementer's judgement call:

- **Accept the migrations.** Correct and complete; costs one bulk migration per app and will
  conflict with any in-flight branch touching the same apps.
- **Defer.** Model names stay English inside translated chrome. Honest, but it is the difference
  between "mostly translated" and "obviously half-translated" on every list and detail page.
- **Split.** Do the ~30 highest-traffic models (Device, Location, Rack, Prefix, IP Address, VLAN,
  Circuit, Interface, ...) now and the long tail later.

Note that wrapping an *existing* `verbose_name` is still migration-invisible -- that was verified in
WB8a and has not changed. Only *adding* one where none existed alters `Meta.original_attrs`.

### Deliberately not translated

Two classes were investigated, found to be reachable in principle, and left in English because
translating them would move a value that is not display-only. Both are recorded here so the question
does not get re-opened from scratch.

- **Job `Meta.name` / `description` / `grouping`** (32 strings across the system jobs). Two
  independent blockers. `Job._get_meta_attr_and_assert_type()` asserts `expected_type=str`, and a
  `gettext_lazy` proxy is not a `str`, so wrapping raises `TypeError` at import. More fundamentally,
  `refresh_job_model_from_job_class()` copies `job_class.name` into `Job.name`, a `CharField` — so
  even a forced string would persist whichever language happened to be active during
  `post_upgrade`, freezing it for every user thereafter and spuriously setting `name_override`.
  Translating job metadata needs a schema change (a display name resolved per request, separate
  from the stored one), not a marking pass.

- **Optgroup headings in grouped `ChoiceSet`s** (`Copper`, `Wireless`, `Ethernet (fixed)`, ~35 of
  them). These are display-only at runtime — Django validates against `c[0]`, and `ChoiceSet.values()`
  unpacks groups — so marking them looked safe, and it renders correctly. But
  `MultipleChoiceFilter(choices=InterfaceTypeChoices)` hands django-filter the *grouped* tuple, and
  drf-spectacular flattens it by taking the group heading as a value: the published schema already
  advertises `"Wireless"` as an accepted `type=` filter value on `/dcim/interface-templates/`, which
  it is not. Marking the headings made that already-wrong enum language-dependent as well
  (`"Wireless"` became `"Funk"` under `de`), so the change was reverted. The underlying schema bug
  is worth a separate issue; the headings can be translated once it is fixed.

- **The *order* of the date/time picker hints.** The placeholders now translate their letters
  (`JJJJ-MM-TT`, `AAAA-MM-JJ`, `年-月-日`) but keep ISO field order, and the translator notes in the
  catalog say so. That is not a stylistic choice: `initializeDateTimePicker()` calls Flatpickr with
  no `dateFormat`, so the picker writes year-month-day into the field in every locale. Django's
  parser meanwhile *prefers* the locale form — under `de`, `DATE_INPUT_FORMATS[0]` is `%d.%m.%Y` and
  `31.12.2025` is accepted — so the two disagree about what a date looks like, and only ISO is
  common to both. Showing `TT.MM.JJJJ` would describe the parser while contradicting the widget.
  Making the order locale-aware means configuring Flatpickr per language *and* changing the hint
  together; it alters what gets submitted, so it needs its own change and its own tests.

The general rule both cases illustrate: a string is safe to mark only if nothing downstream stores
it, compares it, or publishes it as a contract. Rendering correctly is not sufficient evidence.

### High value

0. ~~6479 filter labels remain frozen in English, inside django-filter.~~ **Retracted — this was a
   measurement error, and the labels translate correctly today.** The original finding read
   `FilterSet().filters[name].label` once, under English. That attribute holds a plain `str`
   *computed for whichever language was active at instantiation*, which is indistinguishable from a
   frozen value by inspection — hence the wrong conclusion.

   `label_for_filter()` in fact composes the label fresh on every instantiation, from two pieces
   that are already translatable: the model field's `gettext_lazy` `verbose_name`, and a lookup verb
   from django-filter's own catalog. `base_filters[name].label` is `None`; nothing is cached in
   English. Verified by instantiating inside `translation.override()`:

   ```
   ProviderNetworkFilterSet().filters["comments__ic"].label
     en  'Comments contains'   de  'Kommentare enthält'   fr  'Commentaires contient'
   ```

   No upstream fix is needed and no maintainer judgement is required. `FilterLabelTestCase` guards
   the arrangement, which is breakable from either side: making a field's `verbose_name` a plain
   string, or adding an explicit `label=` that replaces a computed label with a fixed one.

   What *does* remain is ordinary backlog: filters that declare their own label — `label=_("Contacts
   (name or ID)")` and similar — are marked strings awaiting catalog entries, like anything else.

   Measuring this class of question by reading `.label` is unreliable; render under two languages and
   compare instead.


1. **Translation coverage is 49%.** Of 3660 extracted msgids, 1853 are untranslated, predominantly
   `help_text`. They render in English. This is pure translation labour, not engineering. About 40
   of those are Django admin strings that Django itself already translates and should be left
   empty.
2. **Native-speaker review.** No language should be presented as GA before a named reviewer signs
   off. Catalogs carry `X-Translation-Source: machine-assisted (Claude), pending native review`.
3. **CI wiring.** `invoke check-translations` runs under `invoke lint` but CI calls individual
   tasks, and `.github/workflows/` is hook-protected here. A human needs to add it to
   `ci_pullrequest.yml`.

### Medium

1. **The error/flash tranche is now mostly done, not deferred.** The plan scoped this out on the
   assumption that the f-strings needed `ngettext`-aware restructuring first, citing conditional
   verbs chosen inside the string. Measured against `messages.*` calls specifically, that case does
   not occur: of 132 calls, 29 were plain strings and 49 were simple substitution. Both sets are now
   extractable and translated. Only 5 were genuinely unsafe to convert mechanically (format specs,
   a literal `%`, or implicit concatenation) and were left alone with their locations recorded.

   The conditional-verb problem the plan warned about is real, but it lives in `ValidationError`
   strings and other non-`messages` prose -- still untouched, still a larger tranche.
2. **`JobRunButton` hx-vals** uses stdlib `json.dumps` (`object_detail.py` ~2953), which does not
   coerce lazy objects. Those labels are deliberately unwrapped; wrapping one will raise at render.
   Left as a watch item, as the design research specified.
3. **`inc/nav_favorites.html`** shows the stored English `name` even in a localized UI, because
   favorites are persisted by key. A template tag could resolve the current label with the stored
   name as fallback. Never worse than today.
4. **Remaining Phase 0 medium/low gaps** untouched: G-13/G-14 (non-ASCII download filenames),
   G-16 (`open()` without `encoding=`), G-19 (NFC normalization), G-5/G-18 (MySQL collation
   divergence), G-12, G-15, G-17, G-22, G-23.

### Low

1. **CJK typography** — shipped fonts cover Latin/Greek/Cyrillic only; `text-transform: uppercase`
   is a no-op for CJK; `Truncator().words()` never triggers on space-less scripts.
2. **Legacy `project-static/js/`** (~8 strings) not extracted, as scoped.
3. **RTL** — `dir=` is plumbed through and resolves `ltr` for all shipped languages, but no RTL
    stylesheet exists. The cheap enabling work is done; Arabic remains a separate workstream.

---

## 7. How to review this

Read the layers in order; each stands alone and passes `nautobot-server check` on its own.

1. **Layer 1 first.** It resolves the D-1 design conflict that killed the 3.1 attempt. If the
   precedence rule is wrong, nothing downstream matters.
2. **Layer 2.** The only public API change. Check that `name` is never translated and that the
   zero-app-changes regression test says what you want it to say.
3. **Layer 3.** Independently shippable; contains the one product call that needs a decision (§3.1).
4. **Layer 6, ChoiceSet exclusions** (§3.2) — the most judgment-dense part of the diff.
5. **Layers 6 and 7 otherwise are mechanical**, and layer 8 is generated. Skim for pattern
   conformance; the interesting cases are the f-strings converted to named placeholders, since
   those are the ones a translator can reorder.

A few files deliberately appear in two layers — `core/settings.py`, `users/views.py`,
`core/models/fields.py`, `tasks.py` and three templates gain structural changes early and string
marking later. If you rebase, note that `tasks.py` reaches its final form in layer 6, not layer 4.

**Verification performed:**

- `invoke check-migrations` — clean
- `invoke check-schema` — clean, all API versions
- `invoke ruff` / `djhtml` / `djlint` / `markdownlint` / `eslint` / `prettier` — clean
- `invoke check-translations` — clean; `msgfmt --check` passes for all 8 catalogs
- `nautobot-server validate_templates` — no new failures
- Live proof on the dev server: `<html lang>`, nav labels, per-language dates, D-1 override, and
  the Example App zero-change guarantee, in all four languages

**Not run:** Selenium integration tests. `data-section-name`, `hx-vals tab_name`, and favorites
`hx-vals` were deliberately left on the stable `name`, so they should pass, but that is reasoning
rather than evidence and should be confirmed in CI.

---

## 8. Local environment notes

Two gitignored files were created for this machine and are not part of the change:
`invoke.yml` and `development/docker-compose.override.yml` (host port 8080 was occupied; Nautobot
was served on 8480, plus a tailnet `ALLOWED_HOSTS` entry). `mise.toml` and `.venv-invoke/` are
likewise local-only and excluded via `.git/info/exclude`.

`gettext` was added to the dev Dockerfile stage in WB7. Existing containers need a rebuild
(`invoke build`) before `invoke makemessages` will work.
