from django.contrib.contenttypes.models import ContentType
from django.db.models import F
from django.utils.translation import gettext_lazy as _

from nautobot.core.apps import HomePageGroup, HomePageItem, HomePagePanel
from nautobot.dcim import models


def _connected_console_ports_count(request):
    # Match queryset used in dcim.views.ConsoleConnectionsListView
    return (
        models.ConsolePort.objects.restrict(request.user, "view").filter(cable_paths__isnull=False).distinct().count()
    )


def _connected_interfaces_count(request):
    # Match queryset used in dcim.views.InterfaceConnectionsListView. Counts CablePath rows so each
    # connection (including each breakout-cable lane) is one count. Limited to connections where the
    # user has view permission for BOTH endpoint interfaces.
    iface_ct = ContentType.objects.get_for_model(models.Interface)
    visible_ifaces = models.Interface.objects.restrict(request.user, "view").values("pk")
    return models.CablePath.objects.filter(
        origin_type=iface_ct,
        destination_type=iface_ct,
        origin_id__lt=F("destination_id"),
        origin_id__in=visible_ifaces,
        destination_id__in=visible_ifaces,
    ).count()


def _connected_power_ports_count(request):
    # Match queryset used in dcim.views.PowerConnectionsListView
    return models.PowerPort.objects.restrict(request.user, "view").filter(cable_paths__isnull=False).distinct().count()


layout = (
    HomePagePanel(
        name="Organization",
        label=_("Organization"),
        weight=100,
        items=(
            HomePageItem(
                name="Locations",
                label=_("Locations"),
                link="dcim:location_list",
                model=models.Location,
                description=_("Hierarchical geographic locations"),
                permissions=["dcim.view_location"],
                weight=100,
            ),
        ),
    ),
    HomePagePanel(
        name="DCIM",
        label=_("DCIM"),
        weight=200,
        items=(
            HomePageItem(
                name="Racks",
                label=_("Racks"),
                link="dcim:rack_list",
                model=models.Rack,
                description=_("Equipment racks, optionally organized by group"),
                permissions=["dcim.view_rack"],
                weight=100,
            ),
            HomePageItem(
                name="Device Types",
                label=_("Device Types"),
                link="dcim:devicetype_list",
                model=models.DeviceType,
                description=_("Physical hardware models by manufacturer"),
                permissions=["dcim.view_devicetype"],
                weight=200,
            ),
            HomePageItem(
                name="Devices",
                label=_("Devices"),
                link="dcim:device_list",
                model=models.Device,
                description=_("Rack-mounted network equipment, servers, and other devices"),
                permissions=["dcim.view_device"],
                weight=300,
            ),
            HomePageItem(
                name="Virtual Chassis",
                label=_("Virtual Chassis"),
                link="dcim:virtualchassis_list",
                model=models.VirtualChassis,
                permissions=["dcim.view_virtualchassis"],
                description=_("Represents a set of devices which share a common control plane"),
                weight=400,
            ),
            HomePageItem(
                name="Controllers",
                label=_("Controllers"),
                link="dcim:controller_list",
                model=models.Controller,
                permissions=["dcim.view_controller"],
                description=_("Represents a network or SDN (Software-Defined Networking) controllers"),
                weight=500,
            ),
            HomePageItem(
                name="Device Redundancy Groups",
                label=_("Device Redundancy Groups"),
                link="dcim:deviceredundancygroup_list",
                model=models.DeviceRedundancyGroup,
                permissions=["dcim.view_deviceredundancygroup"],
                description=_("Represents a set of devices which operate in a failover/HA group"),
                weight=600,
            ),
            HomePageItem(
                name="Interface Redundancy Groups",
                label=_("Interface Redundancy Groups"),
                link="dcim:interfaceredundancygroup_list",
                model=models.InterfaceRedundancyGroup,
                permissions=["dcim.view_interfaceredundancygroup"],
                description=_("Represents a set of interfaces which operate in a failover/HA group"),
                weight=700,
            ),
            HomePageGroup(
                name="Connections",
                label=_("Connections"),
                weight=800,
                items=(
                    HomePageItem(
                        name="Cables",
                        label=_("Cables"),
                        link="dcim:cable_list",
                        model=models.Cable,
                        permissions=["dcim.view_cable"],
                        weight=100,
                    ),
                    HomePageItem(
                        name="Interfaces",
                        label=_("Interfaces"),
                        custom_template="homepage_connections.html",
                        custom_data={
                            "connections_count": _connected_interfaces_count,
                            "connections_url": "dcim:interface_connections_list",
                            "connections_label": "Interfaces",
                        },
                        permissions=["dcim.view_interface"],
                        weight=200,
                    ),
                    HomePageItem(
                        name="Console",
                        label=_("Console"),
                        custom_template="homepage_connections.html",
                        custom_data={
                            "connections_count": _connected_console_ports_count,
                            "connections_url": "dcim:console_connections_list",
                            "connections_label": "Console",
                        },
                        permissions=["dcim.view_consoleport", "dcim.view_consoleserverport"],
                        weight=300,
                    ),
                    HomePageItem(
                        name="Power",
                        label=_("Power"),
                        custom_template="homepage_connections.html",
                        custom_data={
                            "connections_count": _connected_power_ports_count,
                            "connections_url": "dcim:power_connections_list",
                            "connections_label": "Power",
                        },
                        permissions=["dcim.view_powerport", "dcim.view_poweroutlet"],
                        weight=400,
                    ),
                ),
            ),
        ),
    ),
    HomePagePanel(
        name="Power",
        label=_("Power"),
        weight=300,
        items=(
            HomePageItem(
                name="Power Feeds",
                label=_("Power Feeds"),
                link="dcim:powerfeed_list",
                model=models.PowerFeed,
                description=_("Electrical circuits delivering power from panels"),
                permissions=["dcim.view_powerfeed"],
                weight=100,
            ),
            HomePageItem(
                name="Power Panels",
                label=_("Power Panels"),
                link="dcim:powerpanel_list",
                model=models.PowerPanel,
                description=_("Electrical panels receiving utility power"),
                permissions=["dcim.view_powerpanel"],
                weight=200,
            ),
        ),
    ),
)
