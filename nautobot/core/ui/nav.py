"""Classes and utilities for populating the Nautobot nav menu."""

from abc import ABC, abstractmethod
import logging

from django.utils.http import urlencode

from nautobot.core.choices import ButtonActionColorChoices, ButtonActionIconChoices

from .base import PermissionsMixin

NAV_CONTEXT_NAMES = ("Inventory", "Networks", "Security", "Automation", "Platform")


logger = logging.getLogger(__name__)


class NavMenuBase(ABC):
    """Base class for navigation classes."""

    @property
    @abstractmethod
    def initial_dict(self) -> dict:  # to be implemented by each subclass
        """Attributes to be stored when adding this item to the nav menu data for the first time."""
        return {}

    @property
    @abstractmethod
    def fixed_fields(self) -> tuple:  # to be implemented by subclass
        """Tuple of (name, attribute) entries describing fields that may not be altered after declaration."""
        return ()


class NavMenuTab(NavMenuBase, PermissionsMixin):
    """
    Ths class represents a navigation menu tab. This is built up from a name and a weight value. The name is
    the stable identity of the tab and the weight defines its position in the navbar. The optional label is
    the text actually displayed; when omitted it defaults to the name.

    Groups are each specified as a list of NavMenuGroup instances.
    """

    permissions = []
    groups = []
    label = None

    @property
    def initial_dict(self) -> dict:
        """Attributes to be stored when adding this item to the nav menu data for the first time."""
        return {
            "icon": self.icon,
            "label": self.label if self.label is not None else self.name,
            "weight": self.weight,
            "groups": {},
            "permissions": set(),
        }

    @property
    def fixed_fields(self) -> tuple:
        """Tuple of (name, attribute) entries describing fields that may not be altered after declaration."""
        return ()

    def __init__(self, name, permissions=None, groups=None, weight=1000, icon=None, label=None):
        """
        Ensure tab properties.

        Args:
            name (str): The name of the tab. This is the stable key that apps use to attach groups to
                an existing tab, and that navigation-related preferences are stored against, so it
                must not be translated or otherwise varied.
            permissions (list): The permissions required to view this tab.
            groups (list): List of groups to be rendered in this tab.
            weight (int): The weight of this tab.
            icon (str): The name of the Nautobot icon representing this tab or an SVG static file URL.
            label (str): Text to display for this tab, defaulting to `name`. May be a lazily-translated
                string; it is resolved once per request, under that request's active language.
        """
        super().__init__(permissions)
        self.name = name
        self.weight = weight
        self.icon = icon
        self.label = label

        if groups is not None:
            if not isinstance(groups, (list, tuple)):
                raise TypeError("Groups must be passed as a tuple or list.")
            elif not all(isinstance(group, NavMenuGroup) for group in groups):
                raise TypeError("All groups defined in a tab must be an instance of NavMenuGroup")
            self.groups = groups


class NavMenuGroup(NavMenuBase, PermissionsMixin):
    """
    Ths class represents a navigation menu group. This is built up from a name and a weight value. The name is
    the stable identity of the group and the weight defines its position in the navbar. The optional label is
    the text actually displayed; when omitted it defaults to the name.

    Items are each specified as a list of NavMenuItem instances.
    """

    permissions = []
    items = []
    label = None

    @property
    def initial_dict(self) -> dict:
        """Attributes to be stored when adding this item to the nav menu data for the first time."""
        return {
            "label": self.label if self.label is not None else self.name,
            "weight": self.weight,
            "items": {},
            "permissions": set(),
        }

    @property
    def fixed_fields(self) -> tuple:
        """Tuple of (name, attribute) entries describing fields that may not be altered after declaration."""
        return ()

    def __init__(self, name, items=None, weight=1000, label=None):
        """
        Ensure group properties.

        Args:
            name (str): The name of the group. This is the stable key that apps use to attach items to
                an existing group, so it must not be translated or otherwise varied.
            items (list): List of items to be rendered in this group.
            weight (int): The weight of this group.
            label (str): Text to display for this group, defaulting to `name`. May be a lazily-translated
                string; it is resolved once per request, under that request's active language.
        """
        self.name = name
        self.weight = weight
        self.label = label

        if items is not None and not isinstance(items, (list, tuple)):
            raise TypeError("Items must be passed as a tuple or list.")
        elif not all(isinstance(item, NavMenuItem) for item in items):
            raise TypeError("All items defined in a group must be an instance of NavMenuItem")
        self.items = items
        super().__init__(permissions=self.permissions)


class NavMenuItem(NavMenuBase, PermissionsMixin):
    """
    This class represents a navigation menu item. This constitutes primary link and its text, but also allows for
    specifying additional link buttons that appear to the right of the item in the nav menu.

    Links are specified as Django reverse URL strings.
    Buttons are each specified as a list of NavMenuButton instances.
    """

    @property
    def initial_dict(self) -> dict:
        """Attributes to be stored when adding this item to the nav menu data for the first time."""
        return {
            "name": self.name,
            "label": self.label if self.label is not None else self.name,
            "weight": self.weight,
            "buttons": {},
            "permissions": self.permissions,
            "args": [],
            "kwargs": {},
            "query_params": self.query_params,
        }

    @property
    def fixed_fields(self) -> tuple:
        """Tuple of (name, attribute) entries describing fields that may not be altered after declaration."""
        return (
            ("name", self.name),
            ("permissions", self.permissions),
        )

    permissions = []
    buttons = []
    args = []
    kwargs = {}
    label = None

    def __init__(
        self,
        link,
        name,
        args=None,
        kwargs=None,
        query_params=None,
        permissions=None,
        buttons=(),
        weight=1000,
        label=None,
    ):
        """
        Ensure item properties.

        Args:
            link (str): The link to be used for this item.
            name (str): The name of the item. This is the stable key: it is what gets stored when a
                user favorites this item, so it must not be translated or otherwise varied.
            args (list): Arguments that are being passed to the url with reverse() method
            kwargs (dict): Keyword arguments are are being passed to the url with reverse() method
            query_params (dict): Query parameters to be appended to the URL.
            permissions (list): The permissions required to view this item.
            buttons (list): List of buttons to be rendered in this item.
            weight (int): The weight of this item.
            label (str): Text to display for this item, defaulting to `name`. May be a lazily-translated
                string; it is resolved once per request, under that request's active language.
        """
        super().__init__(permissions)
        self.link = link
        self.name = name
        self.weight = weight
        self.label = label
        self.args = args
        self.kwargs = kwargs
        self.query_params = query_params

        if not isinstance(buttons, (list, tuple)):
            raise TypeError("Buttons must be passed as a tuple or list.")
        elif not all(isinstance(button, NavMenuButton) for button in buttons):
            raise TypeError("All buttons defined in an item must be an instance or subclass of NavMenuButton")
        self.buttons = buttons


class NavMenuButton(NavMenuBase, PermissionsMixin):
    """
    This class represents a button within a NavMenuItem.
    """

    @property
    def initial_dict(self) -> dict:
        """Attributes to be stored when adding this item to the nav menu data for the first time."""
        return {
            "link": self.link,
            "icon_class": self.icon_class,
            "button_class": self.button_class,
            "weight": self.weight,
            "buttons": {},
            "permissions": self.permissions,
            "querystring": self.querystring,
        }

    @property
    def fixed_fields(self) -> tuple:
        """Tuple of (name, attribute) entries describing fields that may not be altered after declaration."""
        return (
            ("button_class", self.button_class),
            ("icon_class", self.icon_class),
            ("link", self.link),
            ("permissions", self.permissions),
        )

    def __init__(
        self,
        link,
        title,
        icon_class,
        button_class=ButtonActionColorChoices.DEFAULT,
        permissions=None,
        weight=1000,
        query_params=None,
    ):
        """
        Ensure button properties.

        Args:
            link (str): The link to be used for this button.
            title (str): The title of the button.
            icon_class (str): The icon class to be used as the icon for the start of the button.
            button_class (str): The button class defines to be used to define the style of the button.
            permissions (list): The permissions required to view this button.
            weight (int): The weight of this button.
            query_params (dict): Query parameters to be appended to the URL.
        """
        super().__init__(permissions)
        self.link = link
        self.title = title
        self.icon_class = icon_class
        self.weight = weight
        self.button_class = button_class
        self.query_params = query_params
        self.querystring = f"?{urlencode(query_params)}" if query_params else ""


class NavMenuAddButton(NavMenuButton):
    """Add button subclass."""

    def __init__(self, *args, **kwargs):
        """Ensure button properties."""
        if "title" not in kwargs:
            kwargs["title"] = "Add"
        if "icon_class" not in kwargs:
            kwargs["icon_class"] = ButtonActionIconChoices.ADD
        if "button_class" not in kwargs:
            kwargs["button_class"] = ButtonActionColorChoices.ADD
        if "weight" not in kwargs:
            kwargs["weight"] = 100
        super().__init__(*args, **kwargs)


class NavMenuImportButton(NavMenuButton):
    """Import button subclass."""

    def __init__(self, *args, **kwargs):
        """Ensure button properties."""
        if "title" not in kwargs:
            kwargs["title"] = "Import"
        if "icon_class" not in kwargs:
            kwargs["icon_class"] = ButtonActionIconChoices.IMPORT
        if "button_class" not in kwargs:
            kwargs["button_class"] = ButtonActionColorChoices.IMPORT
        if "weight" not in kwargs:
            kwargs["weight"] = 200
        super().__init__(*args, **kwargs)
