from django.utils.translation import gettext_lazy as _

from nautobot.core.apps import HomePageItem, HomePagePanel
from nautobot.virtualization.models import Cluster, VirtualMachine

layout = (
    HomePagePanel(
        name="Virtualization",
        label=_("Virtualization"),
        weight=600,
        items=(
            HomePageItem(
                name="Clusters",
                label=_("Clusters"),
                link="virtualization:cluster_list",
                model=Cluster,
                description=_("Clusters of physical hosts in which VMs reside"),
                permissions=["virtualization.view_cluster"],
                weight=100,
            ),
            HomePageItem(
                name="Virtual Machines",
                label=_("Virtual Machines"),
                link="virtualization:virtualmachine_list",
                model=VirtualMachine,
                description=_("Virtual compute instances running inside clusters"),
                permissions=["virtualization.view_virtualmachine"],
                weight=200,
            ),
        ),
    ),
)
