from django.utils.translation import gettext_lazy as _

from nautobot.core.apps import HomePageItem, HomePagePanel
from nautobot.ipam.models import IPAddress, IPAddressRange, Prefix, VLAN, VRF

layout = (
    HomePagePanel(
        name="IPAM",
        label=_("IPAM"),
        weight=400,
        items=(
            HomePageItem(
                name="VRFs",
                label=_("VRFs"),
                link="ipam:vrf_list",
                model=VRF,
                description=_("Virtual routing and forwarding tables"),
                permissions=["ipam.view_vrf"],
                weight=100,
            ),
            HomePageItem(
                name="Prefixes",
                label=_("Prefixes"),
                link="ipam:prefix_list",
                model=Prefix,
                description=_("IPv4 and IPv6 network assignments"),
                permissions=["ipam.view_prefix"],
                weight=300,
            ),
            HomePageItem(
                name="IP Addresses",
                label=_("IP Addresses"),
                link="ipam:ipaddress_list",
                model=IPAddress,
                description=_("IPv4 and IPv6 network assignments"),
                permissions=["ipam.view_ipaddress"],
                weight=400,
            ),
            HomePageItem(
                name="IP Address Ranges",
                label=_("IP Address Ranges"),
                link="ipam:ipaddressrange_list",
                model=IPAddressRange,
                description=_("Contiguous spans of IP addresses within a prefix"),
                permissions=["ipam.view_ipaddressrange"],
                weight=450,
            ),
            HomePageItem(
                name="VLAN",
                label=_("VLAN"),
                link="ipam:vlan_list",
                model=VLAN,
                description=_("Layer two domains, identified by VLAN ID"),
                permissions=["ipam.view_vlan"],
                weight=500,
            ),
        ),
    ),
)
