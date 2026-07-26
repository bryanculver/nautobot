from django.utils.translation import gettext_lazy as _, gettext_noop
import django_tables2 as tables

from nautobot.core.tables import (
    BaseTable,
    ButtonsColumn,
    LinkedCountColumn,
    TagColumn,
    ToggleColumn,
)
from nautobot.dcim.tables.devices import BaseInterfaceTable
from nautobot.extras.tables import RoleTableMixin, StatusTableMixin
from nautobot.tenancy.tables import TenantColumn

from .models import Cluster, ClusterGroup, ClusterType, VirtualMachine, VMInterface

__all__ = (
    "ClusterGroupTable",
    "ClusterTable",
    "ClusterTypeTable",
    "VMInterfaceTable",
    "VirtualMachineDetailTable",
    "VirtualMachineTable",
    "VirtualMachineVMInterfaceTable",
)

# See `nautobot.core.ui.titles`: a template fragment in a Python literal is invisible to
# `makemessages`, so its msgid is declared here.
TRANSLATABLE_FRAGMENT_MESSAGES = (gettext_noop("Add IP address"),)


VMINTERFACE_BUTTONS = """
{% load i18n %}
{% if perms.ipam.add_ipaddress and perms.virtualization.change_vminterface %}
    <li>
        <a href="{% url 'ipam:ipaddress_add' %}?vminterface={{ record.pk }}&return_url={{ request.path }}" class="dropdown-item text-success">
            <span class="mdi mdi-plus-thick" aria-hidden="true"></span>
            {% trans "Add IP address" %}
        </a>
    </li>
{% endif %}
"""


#
# Cluster types
#


class ClusterTypeTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()
    cluster_count = LinkedCountColumn(
        viewname="virtualization:cluster_list", url_params={"cluster_type": "pk"}, verbose_name=_("Clusters")
    )
    actions = ButtonsColumn(ClusterType)

    class Meta(BaseTable.Meta):
        model = ClusterType
        fields = ("pk", "name", "cluster_count", "description", "actions")
        default_columns = ("pk", "name", "cluster_count", "description", "actions")


#
# Cluster groups
#


class ClusterGroupTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()
    cluster_count = LinkedCountColumn(
        viewname="virtualization:cluster_list", url_params={"cluster_group": "pk"}, verbose_name=_("Clusters")
    )
    actions = ButtonsColumn(ClusterGroup)

    class Meta(BaseTable.Meta):
        model = ClusterGroup
        fields = ("pk", "name", "cluster_count", "description", "actions")
        default_columns = ("pk", "name", "cluster_count", "description", "actions")


#
# Clusters
#


class ClusterTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()
    tenant = tables.Column(linkify=True)
    cluster_type = tables.Column(linkify=True, verbose_name=_("Cluster Type"))
    cluster_group = tables.Column(linkify=True, verbose_name=_("Cluster Group"))
    device_count = LinkedCountColumn(
        viewname="dcim:device_list",
        url_params={"clusters": "pk"},
        reverse_lookup="clusters",
        verbose_name=_("Devices"),
    )
    vm_count = LinkedCountColumn(
        viewname="virtualization:virtualmachine_list",
        url_params={"cluster": "pk"},
        verbose_name=_("VMs"),
    )
    tags = TagColumn(url_name="virtualization:cluster_list")

    class Meta(BaseTable.Meta):
        model = Cluster
        fields = (
            "pk",
            "name",
            "cluster_type",
            "cluster_group",
            "tenant",
            "device_count",
            "vm_count",
            "tags",
        )
        default_columns = (
            "pk",
            "name",
            "cluster_type",
            "cluster_group",
            "tenant",
            "device_count",
            "vm_count",
        )


#
# Virtual machines
#


class VirtualMachineTable(StatusTableMixin, RoleTableMixin, BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()
    cluster = tables.Column(linkify=True)
    tenant = TenantColumn()
    actions = ButtonsColumn(VirtualMachine)

    class Meta(BaseTable.Meta):
        model = VirtualMachine
        fields = (
            "pk",
            "name",
            "status",
            "cluster",
            "role",
            "tenant",
            "vcpus",
            "memory",
            "disk",
            "actions",
        )


class VirtualMachineDetailTable(VirtualMachineTable):
    primary_ip4 = tables.Column(linkify=True, verbose_name=_("IPv4 Address"))
    primary_ip6 = tables.Column(linkify=True, verbose_name=_("IPv6 Address"))
    primary_ip = tables.Column(linkify=True, verbose_name=_("IP Address"), order_by=("primary_ip6", "primary_ip4"))
    tags = TagColumn(url_name="virtualization:virtualmachine_list")

    class Meta(BaseTable.Meta):
        model = VirtualMachine
        fields = (
            "pk",
            "name",
            "status",
            "cluster",
            "role",
            "tenant",
            "platform",
            "vcpus",
            "memory",
            "disk",
            "primary_ip4",
            "primary_ip6",
            "primary_ip",
            "tags",
        )
        default_columns = (
            "pk",
            "name",
            "status",
            "cluster",
            "role",
            "tenant",
            "vcpus",
            "memory",
            "disk",
            "primary_ip",
        )


#
# VM components
#


class VMInterfaceTable(BaseInterfaceTable):
    pk = ToggleColumn()
    virtual_machine = tables.LinkColumn()
    name = tables.Column(linkify=True)
    tags = TagColumn(url_name="virtualization:vminterface_list")
    actions = ButtonsColumn(VMInterface)

    class Meta(BaseTable.Meta):
        model = VMInterface
        fields = (
            "pk",
            "virtual_machine",
            "name",
            "status",
            "role",
            "enabled",
            "mac_address",
            "mtu",
            "mode",
            "description",
            "tags",
            "ip_addresses",
            "untagged_vlan",
            "tagged_vlans",
            "actions",
        )
        default_columns = ("pk", "virtual_machine", "name", "status", "role", "enabled", "description", "actions")


class VirtualMachineVMInterfaceTable(VMInterfaceTable):
    parent_interface = tables.Column(linkify=True)
    bridge = tables.Column(linkify=True)
    actions = ButtonsColumn(
        model=VMInterface,
        buttons=("edit", "delete"),
        prepend_template=VMINTERFACE_BUTTONS,
    )

    class Meta(BaseTable.Meta):
        model = VMInterface
        fields = (
            "pk",
            "name",
            "status",
            "role",
            "enabled",
            "parent_interface",
            "bridge",
            "mac_address",
            "mtu",
            "mode",
            "description",
            "tags",
            "ip_addresses",
            "untagged_vlan",
            "tagged_vlans",
            "actions",
        )
        default_columns = (
            "pk",
            "name",
            "status",
            "role",
            "enabled",
            "parent_interface",
            "mac_address",
            "mtu",
            "mode",
            "description",
            "ip_addresses",
            "actions",
        )
        row_attrs = {
            "data-name": lambda record: record.name,
        }
