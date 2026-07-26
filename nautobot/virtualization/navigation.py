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
        name="Virtualization",
        label=_("Virtualization"),
        icon=NavigationIconChoices.VIRTUALIZATION,
        weight=NavigationWeightChoices.VIRTUALIZATION,
        groups=(
            NavMenuGroup(
                name="Virtual Machines",
                label=_("Virtual Machines"),
                weight=100,
                items=(
                    NavMenuItem(
                        link="virtualization:virtualmachine_list",
                        name="Virtual Machines",
                        label=_("Virtual Machines"),
                        weight=100,
                        permissions=[
                            "virtualization.view_virtualmachine",
                        ],
                        buttons=(
                            NavMenuAddButton(
                                link="virtualization:virtualmachine_add",
                                permissions=[
                                    "virtualization.add_virtualmachine",
                                ],
                            ),
                        ),
                    ),
                    NavMenuItem(
                        link="virtualization:vminterface_list",
                        name="Interfaces",
                        label=_("Interfaces"),
                        weight=200,
                        permissions=[
                            "virtualization.view_vminterface",
                        ],
                        buttons=(),
                    ),
                ),
            ),
            NavMenuGroup(
                name="Clusters",
                label=_("Clusters"),
                weight=200,
                items=(
                    NavMenuItem(
                        link="virtualization:cluster_list",
                        name="Clusters",
                        label=_("Clusters"),
                        weight=100,
                        permissions=[
                            "virtualization.view_cluster",
                        ],
                        buttons=(
                            NavMenuAddButton(
                                link="virtualization:cluster_add",
                                permissions=[
                                    "virtualization.add_cluster",
                                ],
                            ),
                        ),
                    ),
                    NavMenuItem(
                        link="virtualization:clustertype_list",
                        name="Cluster Types",
                        label=_("Cluster Types"),
                        weight=200,
                        permissions=[
                            "virtualization.view_clustertype",
                        ],
                        buttons=(
                            NavMenuAddButton(
                                link="virtualization:clustertype_add",
                                permissions=[
                                    "virtualization.add_clustertype",
                                ],
                            ),
                        ),
                    ),
                    NavMenuItem(
                        link="virtualization:clustergroup_list",
                        name="Cluster Groups",
                        label=_("Cluster Groups"),
                        weight=300,
                        permissions=[
                            "virtualization.view_clustergroup",
                        ],
                        buttons=(
                            NavMenuAddButton(
                                link="virtualization:clustergroup_add",
                                permissions=[
                                    "virtualization.add_clustergroup",
                                ],
                            ),
                        ),
                    ),
                ),
            ),
        ),
    ),
)
