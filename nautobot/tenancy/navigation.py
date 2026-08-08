from django.utils.translation import gettext_lazy as _

from nautobot.core.apps import (
    NavMenuAddButton,
    NavMenuGroup,
    NavMenuItem,
    NavMenuTab,
)
from nautobot.core.ui.choices import NavigationIconChoices, NavigationWeightChoices

menu_items = (
    NavMenuTab(
        name="Organization",
        label=_("Organization"),
        icon=NavigationIconChoices.ORGANIZATION,
        weight=NavigationWeightChoices.ORGANIZATION,
        groups=(
            NavMenuGroup(
                name="Tenancy",
                label=_("Tenancy"),
                weight=300,
                items=(
                    NavMenuItem(
                        link="tenancy:tenant_list",
                        name="Tenants",
                        label=_("Tenants"),
                        weight=100,
                        permissions=[
                            "tenancy.view_tenant",
                        ],
                        buttons=(
                            NavMenuAddButton(
                                link="tenancy:tenant_add",
                                permissions=[
                                    "tenancy.add_tenant",
                                ],
                            ),
                        ),
                    ),
                    NavMenuItem(
                        link="tenancy:tenantgroup_list",
                        name="Tenant Groups",
                        label=_("Tenant Groups"),
                        weight=200,
                        permissions=[
                            "tenancy.view_tenantgroup",
                        ],
                        buttons=(
                            NavMenuAddButton(
                                link="tenancy:tenantgroup_add",
                                permissions=[
                                    "tenancy.add_tenantgroup",
                                ],
                            ),
                        ),
                    ),
                ),
            ),
        ),
    ),
)
