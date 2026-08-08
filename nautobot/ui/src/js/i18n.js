/**
 * Thin wrapper over the Django JavaScript translation catalog served at `/jsi18n/`.
 *
 * `django.views.i18n.JavaScriptCatalog` installs a global `django` object exposing `gettext`,
 * `ngettext`, and `interpolate`. Everything here degrades to the untranslated English source string
 * if that catalog has not loaded -- a missing or failed catalog request must not take the page down,
 * and `nautobot.js` is also loaded in contexts (tests, error pages) where the catalog is absent.
 *
 * Strings passed to these functions are extracted by `invoke makemessages`, which scans the webpack
 * sources under the `djangojs` domain. Only literal strings are extractable: interpolate rather than
 * building a message out of concatenated fragments.
 */

const catalog = () => (typeof globalThis.django === 'undefined' ? null : globalThis.django);

/**
 * Translate a string into the user's active language.
 *
 * @param {string} text - The English source string; must be a literal for extraction to find it.
 * @returns {string} The translation, or `text` unchanged if there is no catalog or no translation.
 */
export const gettext = (text) => catalog()?.gettext(text) ?? text;

/**
 * Translate a string with a count-dependent plural form.
 *
 * @param {string} singular - The English singular source string.
 * @param {string} plural - The English plural source string.
 * @param {number} count - The count deciding which plural form applies.
 * @returns {string} The appropriate translated form, falling back to English.
 */
export const ngettext = (singular, plural, count) =>
  catalog()?.ngettext(singular, plural, count) ?? (count === 1 ? singular : plural);

/**
 * Fill named `%(name)s` placeholders in a (usually already translated) string.
 *
 * Placeholders are used rather than concatenation because word order differs between languages, so
 * a translator has to be able to move the inserted value within the sentence.
 *
 * @param {string} text - String containing `%(name)s` placeholders.
 * @param {Object} values - Mapping of placeholder name to replacement value.
 * @returns {string} The interpolated string.
 */
export const interpolate = (text, values) =>
  text.replace(/%\(([^)]+)\)s/g, (match, name) => (name in values ? values[name] : match));
