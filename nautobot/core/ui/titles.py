from typing import Literal, Optional, Union

from django.template import Context, Template
from django.utils.html import strip_tags
from django.utils.translation import gettext_noop

# The prose in DEFAULT_TITLES below lives inside `{% blocktrans %}` tags, because these strings are
# rendered as Django templates and several of them need template filters. `makemessages` cannot see
# template tags inside a Python string literal, though, so the same messages are declared here with
# `gettext_noop` purely so that extraction finds them.
#
# `TitlesTestCase.test_translatable_titles_are_extractable` asserts the two stay in sync, so this
# duplication cannot silently drift.
TRANSLATABLE_TITLE_MESSAGES = (
    gettext_noop("Delete %(verbose_name)s?"),
    gettext_noop("Add a new %(verbose_name)s"),
    gettext_noop("Editing %(verbose_name)s %(object)s"),
    gettext_noop("Delete %(count)s %(verbose_name_plural)s?"),
    gettext_noop("Renaming %(count)s %(verbose_name_plural)s on %(parent_name)s"),
    gettext_noop("Editing %(count)s %(verbose_name_plural)s"),
    gettext_noop("Approve %(verbose_name)s?"),
    gettext_noop("Deny %(verbose_name)s?"),
)

DEFAULT_TITLES: dict[str, str] = {
    # No prose, so nothing to translate -- the model's own verbose_name is already translatable.
    "*": "{{ verbose_name_plural|bettertitle }}",
    "list": "{{ verbose_name_plural|bettertitle }}",
    "detail": "{{ object.page_title|default:object }}",
    "retrieve": "{{ object.page_title|default:object }}",
    # Prose: wrapped so word order can differ by language.
    "destroy": "{% blocktrans with verbose_name=verbose_name %}Delete {{ verbose_name }}?{% endblocktrans %}",
    "create": "{% blocktrans with verbose_name=verbose_name %}Add a new {{ verbose_name }}{% endblocktrans %}",
    "update": (
        "{% with object_title=object.page_title|default:object %}"
        "{% blocktrans with verbose_name=verbose_name object=object_title %}"
        "Editing {{ verbose_name }} {{ object }}{% endblocktrans %}{% endwith %}"
    ),
    "bulk_destroy": (
        "{% with plural=verbose_name_plural|bettertitle %}"
        "{% blocktrans with count=total_objs_to_delete verbose_name_plural=plural %}"
        "Delete {{ count }} {{ verbose_name_plural }}?{% endblocktrans %}{% endwith %}"
    ),
    "bulk_rename": (
        "{% with plural=verbose_name_plural|bettertitle count=selected_objects|length %}"
        "{% blocktrans with count=count verbose_name_plural=plural parent_name=parent_name %}"
        "Renaming {{ count }} {{ verbose_name_plural }} on {{ parent_name }}{% endblocktrans %}{% endwith %}"
    ),
    "bulk_update": (
        "{% with plural=verbose_name_plural|bettertitle %}"
        "{% blocktrans with count=objs_count verbose_name_plural=plural %}"
        "Editing {{ count }} {{ verbose_name_plural }}{% endblocktrans %}{% endwith %}"
    ),
    "approve": (
        "{% with name=verbose_name|bettertitle %}"
        "{% blocktrans with verbose_name=name %}Approve {{ verbose_name }}?{% endblocktrans %}{% endwith %}"
    ),
    "deny": (
        "{% with name=verbose_name|bettertitle %}"
        "{% blocktrans with verbose_name=name %}Deny {{ verbose_name }}?{% endblocktrans %}{% endwith %}"
    ),
}

DEFAULT_PLUGINS = ["helpers", "i18n"]

ModeType = Literal["html", "plain"]


class Titles:
    """
    Base class for document titles and page headings.

    This class provides a mechanism to define per-action title templates.
    Titles can be dynamically rendered using context variables and template tags using the Django template engine and context.
    Use the `render()` method to obtain either rich (HTML) or plain (stripped of HTML) output.

    There is a dedicated simple tag to render `Titles` passed in the `context['view_titles']`: `{% render_title mode="html" %}`

    Attributes:
        titles (dict[str, str]): Action-to-title-template mapping.
        template_plugins (list[str]): List of Django template libraries to load before rendering.

    Args:
        template_plugins (Optional[list[str]]): Template libraries to load into rendering.
        titles (dict): Action-to-template-string mappings that override or extend the defaults.
    """

    def __init__(self, template_plugins: Optional[list[str]] = None, titles: Optional[dict[str, str]] = None):
        """
        Keyword arguments passed can either add new action-title pair or override existing titles.

        Args:
            template_plugins (Optional[list[str]]): Extra Django template libraries to load before rendering.
            titles (Optional[dict[str, str]]): Custom or overriding mappings from action to template string.
        """
        self.titles: dict[str, str] = DEFAULT_TITLES.copy()
        if titles:
            self.titles.update(**titles)

        self.template_plugins: list[str] = DEFAULT_PLUGINS.copy()
        if template_plugins:
            self.template_plugins.extend(template_plugins)

    def render(self, context: Union[dict, Context], mode: ModeType = "html") -> str:
        """
        Renders the title based on given context and current action.

        If mode == "plain", the output will be stripped of HTML tags.

        Make sure that needed context variables are in context and needed plugins are loaded.

        Args:
            context (Union[dict, Context]): Render context.
            mode (ModeType): Rendering mode: "html" or "plain".

        Returns:
            (str): HTML fragment or plain text, depending on `mode`.
        """
        if isinstance(context, dict):
            context = Context(context)

        with context.update(self.get_extra_context(context)):
            template_str = self.get_template_str(context)
            template = Template(self.template_plugins_str + template_str)
            rendered_title = template.render(context)
            if mode == "plain":
                return strip_tags(rendered_title)
            return rendered_title

    def get_template_str(self, context: Context) -> str:
        """
        Determine the template string for the current action.

        Args:
            context (Context): Render context.

        Returns:
            str: The template string for the current action, or an empty string if not found.
        """
        action = context.get("view_action", "")

        template_str = self.titles.get(action)
        if template_str:
            return template_str

        detail = context.get("detail", False)
        if detail:
            return self.titles.get("detail", "")

        return self.titles.get("*", "")

    @property
    def template_plugins_str(self) -> str:
        """
        Return a concatenated string of Django {% load ... %} tags for all template plugins.

        Returns:
            str: String containing {% load ... %} tags for the required template libraries.
        """
        return "".join(f"{{% load {plugin_name} %}}" for plugin_name in self.template_plugins)

    def get_extra_context(self, context: Context) -> dict:
        """
        Provide additional data to include in the rendering context, based on the configuration of this component.

        Args:
            context (Context): The current template context.

        Returns:
            (dict): Additional context data.
        """
        return {}
