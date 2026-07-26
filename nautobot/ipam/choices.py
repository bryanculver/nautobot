from django.utils.translation import gettext_lazy as _

from nautobot.core.choices import ChoiceSet


class IPAddressVersionChoices(ChoiceSet):
    VERSION_4 = 4
    VERSION_6 = 6

    CHOICES = (
        (VERSION_4, "IPv4"),
        (VERSION_6, "IPv6"),
    )


#
# Prefixes
#


class PrefixStatusChoices(ChoiceSet):
    STATUS_ACTIVE = "active"
    STATUS_RESERVED = "reserved"
    STATUS_DEPRECATED = "deprecated"

    CHOICES = (
        (STATUS_ACTIVE, _("Active")),
        (STATUS_RESERVED, _("Reserved")),
        (STATUS_DEPRECATED, _("Deprecated")),
    )


class PrefixTypeChoices(ChoiceSet):
    TYPE_CONTAINER = "container"
    TYPE_NETWORK = "network"
    TYPE_POOL = "pool"

    CHOICES = (
        (TYPE_CONTAINER, _("Container")),
        (TYPE_NETWORK, _("Network")),
        (TYPE_POOL, _("Pool")),
    )


#
# IPAddresses
#


class IPAddressStatusChoices(ChoiceSet):
    STATUS_ACTIVE = "active"
    STATUS_RESERVED = "reserved"
    STATUS_DEPRECATED = "deprecated"

    CHOICES = (
        (STATUS_ACTIVE, _("Active")),
        (STATUS_RESERVED, _("Reserved")),
        (STATUS_DEPRECATED, _("Deprecated")),
    )


class IPAddressRoleChoices(ChoiceSet):
    ROLE_LOOPBACK = "loopback"
    ROLE_SECONDARY = "secondary"
    ROLE_ANYCAST = "anycast"
    ROLE_VIP = "vip"
    ROLE_VRRP = "vrrp"
    ROLE_HSRP = "hsrp"
    ROLE_GLBP = "glbp"
    ROLE_CARP = "carp"

    CHOICES = (
        (ROLE_LOOPBACK, "Loopback"),
        (ROLE_SECONDARY, "Secondary"),
        (ROLE_ANYCAST, "Anycast"),
        (ROLE_VIP, "VIP"),
        (ROLE_VRRP, "VRRP"),
        (ROLE_HSRP, "HSRP"),
        (ROLE_GLBP, "GLBP"),
        (ROLE_CARP, "CARP"),
    )

    CSS_CLASSES = {
        ROLE_LOOPBACK: "default",
        ROLE_SECONDARY: "primary",
        ROLE_ANYCAST: "warning",
        ROLE_VIP: "success",
        ROLE_VRRP: "success",
        ROLE_HSRP: "success",
        ROLE_GLBP: "success",
        ROLE_CARP: "success",
    }


class IPAddressTypeChoices(ChoiceSet):
    TYPE_DHCP = "dhcp"
    TYPE_HOST = "host"
    TYPE_SLAAC = "slaac"

    CHOICES = (
        (TYPE_DHCP, _("DHCP")),
        (TYPE_HOST, _("Host")),
        (TYPE_SLAAC, _("SLAAC")),
    )


#
# IPAddressRange
#


class IPAddressRangeStatusChoices(ChoiceSet):
    STATUS_ACTIVE = "active"
    STATUS_RESERVED = "reserved"
    STATUS_DEPRECATED = "deprecated"

    CHOICES = (
        (STATUS_ACTIVE, _("Active")),
        (STATUS_RESERVED, _("Reserved")),
        (STATUS_DEPRECATED, _("Deprecated")),
    )


class IPAddressRangeRoleChoices(ChoiceSet):
    """Default roles for IPAddressRange objects."""

    ROLE_DHCP = "dhcp"
    ROLE_FIREWALL_OBJECT = "firewall-object"
    ROLE_NAT_POOL = "nat-pool"
    ROLE_LOAD_BALANCER_POOL = "load-balancer-pool"
    ROLE_RESERVED = "reserved"

    CHOICES = (
        (ROLE_DHCP, _("DHCP")),
        (ROLE_FIREWALL_OBJECT, _("Firewall Object")),
        (ROLE_NAT_POOL, _("NAT Pool")),
        (ROLE_LOAD_BALANCER_POOL, _("Load Balancer Pool")),
        (ROLE_RESERVED, _("Reserved")),
    )


#
# VRFs
#


class VRFStatusChoices(ChoiceSet):
    STATUS_ACTIVE = "active"
    STATUS_DOWN = "down"
    STATUS_DEPRECATED = "deprecated"

    CHOICES = (
        (STATUS_ACTIVE, _("Active")),
        (STATUS_DOWN, _("Down")),
        (STATUS_DEPRECATED, _("Deprecated")),
    )


#
# VLANs
#


class VLANStatusChoices(ChoiceSet):
    STATUS_ACTIVE = "active"
    STATUS_RESERVED = "reserved"
    STATUS_DEPRECATED = "deprecated"

    CHOICES = (
        (STATUS_ACTIVE, _("Active")),
        (STATUS_RESERVED, _("Reserved")),
        (STATUS_DEPRECATED, _("Deprecated")),
    )


#
# Services
#


class ServiceProtocolChoices(ChoiceSet):
    PROTOCOL_TCP = "tcp"
    PROTOCOL_UDP = "udp"

    CHOICES = (
        (PROTOCOL_TCP, "TCP"),
        (PROTOCOL_UDP, "UDP"),
    )
