from django.utils.translation import gettext_lazy as _

from nautobot.core.apps import HomePageItem, HomePagePanel
from nautobot.wireless.models import WirelessNetwork

layout = (
    HomePagePanel(
        name="Wireless",
        label=_("Wireless"),
        weight=500,
        items=(
            HomePageItem(
                name="Wireless Networks",
                label=_("Wireless Networks"),
                link="wireless:wirelessnetwork_list",
                model=WirelessNetwork,
                description=_("Wireless networks for access points"),
                permissions=["wireless.view_wirelessnetwork"],
                weight=100,
            ),
        ),
    ),
)
