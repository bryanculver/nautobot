from django.utils.translation import gettext_lazy as _

from nautobot.core.apps import HomePageItem, HomePagePanel
from nautobot.vpn.models import VPN, VPNTunnel, VPNTunnelEndpoint

layout = (
    HomePagePanel(
        name="VPN",
        label=_("VPN"),
        weight=550,
        items=(
            HomePageItem(
                name="VPNs",
                label=_("VPNs"),
                link="vpn:vpn_list",
                model=VPN,
                description=_("VPNs"),
                permissions=["vpn.view_vpn"],
                weight=100,
            ),
            HomePageItem(
                name="VPN Tunnels",
                label=_("VPN Tunnels"),
                link="vpn:vpntunnel_list",
                model=VPNTunnel,
                description=_("VPN Tunnels"),
                permissions=["vpn.view_vpntunnel"],
                weight=200,
            ),
            HomePageItem(
                name="VPN Tunnel Endpoints",
                label=_("VPN Tunnel Endpoints"),
                link="vpn:vpntunnelendpoint_list",
                model=VPNTunnelEndpoint,
                description=_("VPN Tunnel Endpoints"),
                permissions=["vpn.view_vpntunnelendpoint"],
                weight=300,
            ),
        ),
    ),
)
