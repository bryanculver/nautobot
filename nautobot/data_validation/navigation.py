"""App navigation menu items."""

from django.utils.translation import gettext_lazy as _

from nautobot.apps.ui import NavMenuAddButton, NavMenuGroup, NavMenuItem, NavMenuTab
from nautobot.core.ui.choices import NavigationIconChoices, NavigationWeightChoices

menu_items = (
    NavMenuTab(
        name="Extensibility",
        label=_("Extensibility"),
        icon=NavigationIconChoices.EXTENSIBILITY,
        weight=NavigationWeightChoices.EXTENSIBILITY,
        groups=(
            NavMenuGroup(
                name="Data Validation",
                label=_("Data Validation"),
                weight=200,
                items=(
                    NavMenuItem(
                        link="data_validation:minmaxvalidationrule_list",
                        name="Min/Max Rules",
                        label=_("Min/Max Rules"),
                        permissions=["data_validation.view_minmaxvalidationrule"],
                        buttons=(
                            NavMenuAddButton(
                                link="data_validation:minmaxvalidationrule_add",
                                permissions=["data_validation.add_minmaxvalidationrule"],
                            ),
                        ),
                    ),
                    NavMenuItem(
                        link="data_validation:regularexpressionvalidationrule_list",
                        name="Regex Rules",
                        label=_("Regex Rules"),
                        permissions=["data_validation.view_regularexpressionvalidationrule"],
                        buttons=(
                            NavMenuAddButton(
                                link="data_validation:regularexpressionvalidationrule_add",
                                permissions=["data_validation.add_regularexpressionvalidationrule"],
                            ),
                        ),
                    ),
                    NavMenuItem(
                        link="data_validation:requiredvalidationrule_list",
                        name="Required Rules",
                        label=_("Required Rules"),
                        permissions=["data_validation.view_requiredvalidationrule"],
                        buttons=(
                            NavMenuAddButton(
                                link="data_validation:requiredvalidationrule_add",
                                permissions=["data_validation.add_requiredvalidationrule"],
                            ),
                        ),
                    ),
                    NavMenuItem(
                        link="data_validation:uniquevalidationrule_list",
                        name="Unique Rules",
                        label=_("Unique Rules"),
                        permissions=["data_validation.view_uniquevalidationrule"],
                        buttons=(
                            NavMenuAddButton(
                                link="data_validation:uniquevalidationrule_add",
                                permissions=["data_validation.add_uniquevalidationrule"],
                            ),
                        ),
                    ),
                    NavMenuItem(
                        link="data_validation:datacompliance_list",
                        name="Data Compliance",
                        label=_("Data Compliance"),
                        permissions=["data_validation.view_datacompliance"],
                    ),
                    NavMenuItem(
                        link="data_validation:device-constraints",
                        name="Device Constraints",
                        label=_("Device Constraints"),
                        permissions=["dcim.view_device"],
                    ),
                ),
            ),
        ),
    ),
)
