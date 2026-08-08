# Adding Navigation Menu Items

Apps can extend the existing navigation bar layout. By default, Nautobot looks for a `menu_items` list inside of `navigation.py`. (This can be overridden by setting `menu_items` to a custom value on the app's `NautobotAppConfig`.)

Using a key and weight system, a developer can integrate the app's menu additions amongst existing menu tabs, groups, and items.

More documentation and examples can be found in the [Navigation Menu](../../../core/navigation-menu.md) guide.

!!! tip
    To reduce the amount of clutter in the navigation menu, if your app provides an "app configuration" view, we recommend [linking it from the main "Installed Apps" page](../configuration-view.md) rather than adding it as a separate item in the navigation menu.

    Similarly, if your app provides an "app home" or "dashboard" view, consider linking it from the "Installed Apps" page, and/or adding a link from the Nautobot home page (see below), rather than adding it to the navigation menu.

## Translatable Menu Labels

+++ 3.2.0

`NavMenuTab`, `NavMenuGroup`, and `NavMenuItem` accept an optional `label` argument holding the text
actually displayed in the navigation menu. When omitted it defaults to `name`, so **existing apps
require no changes** and render exactly as before.

```python
from django.utils.translation import gettext_lazy as _

from nautobot.apps.ui import NavMenuGroup, NavMenuItem, NavMenuTab

menu_items = (
    NavMenuTab(
        name="My App",
        label=_("My App"),
        groups=(
            NavMenuGroup(
                name="Widgets",
                label=_("Widgets"),
                items=(
                    NavMenuItem(
                        link="my_app:widget_list",
                        name="Widgets",
                        label=_("Widgets"),
                        permissions=["my_app.view_widget"],
                    ),
                ),
            ),
        ),
    ),
)
```

!!! warning "`name` is a key, not display text"
    Do not translate `name`, and do not vary it by language. It is:

    - the key apps use to attach groups and items to an existing tab, so a translated `name` would
      no longer match the tab you meant to extend;
    - what is persisted when a user marks an item as a navigation favorite;
    - what integration tests and the `data-section-name` attribute select on.

    Only `label` is translated, and it is resolved once per request under that request's active
    language. Passing a `gettext_lazy` object is correct and costs nothing until it is rendered.

!!! note
    Translated labels require your App to ship its own translation catalogs. See
    [Shipping Translations from an App](../translations.md); a label with no matching catalog entry
    renders in English, exactly as it does today.
