from django.utils.translation import gettext_lazy as _
import django_filters

from nautobot.circuits.models import Circuit
from nautobot.core.filters import (
    NameSearchFilterSet,
    NaturalKeyOrPKMultipleChoiceFilter,
    RelatedMembershipBooleanFilter,
    SearchFilter,
    TreeNodeMultipleChoiceFilter,
)
from nautobot.dcim.models import Device, Location, Rack, RackReservation
from nautobot.extras.filters import NautobotFilterSet
from nautobot.ipam.filter_mixins import PrefixFilter
from nautobot.ipam.models import IPAddress, RouteTarget, VLAN, VRF
from nautobot.tenancy.filter_mixins import TenancyModelFilterSetMixin
from nautobot.tenancy.models import Tenant, TenantGroup
from nautobot.virtualization.models import Cluster, VirtualMachine

__all__ = (
    "TenancyModelFilterSetMixin",
    "TenantFilterSet",
    "TenantGroupFilterSet",
)


class TenantGroupFilterSet(NautobotFilterSet, NameSearchFilterSet):
    parent = NaturalKeyOrPKMultipleChoiceFilter(
        queryset=TenantGroup.objects.all(),
        label=_("Parent tenant group (name or ID)"),
        to_field_name="name",
    )
    children = NaturalKeyOrPKMultipleChoiceFilter(
        queryset=TenantGroup.objects.all(),
        label=_("Children (name or ID)"),
        to_field_name="name",
    )
    has_children = RelatedMembershipBooleanFilter(
        field_name="children",
        label=_("Has children"),
    )
    tenants = NaturalKeyOrPKMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        label=_("Tenants (name or ID)"),
        to_field_name="name",
    )
    has_tenants = RelatedMembershipBooleanFilter(
        field_name="tenants",
        label=_("Has tenants"),
    )

    class Meta:
        model = TenantGroup
        fields = ["id", "name", "description"]


class TenantFilterSet(NautobotFilterSet):
    q = SearchFilter(
        filter_predicates={
            "name": "icontains",
            "description": "icontains",
            "comments": "icontains",
        },
    )
    tenant_group = TreeNodeMultipleChoiceFilter(
        queryset=TenantGroup.objects.all(),
        field_name="tenant_group",
        label=_("Tenant group (name or ID)"),
        to_field_name="name",
    )
    circuits = django_filters.ModelMultipleChoiceFilter(
        queryset=Circuit.objects.all(),
        label=_("Circuits (ID)"),
    )
    has_circuits = RelatedMembershipBooleanFilter(
        field_name="circuits",
        label=_("Has circuits"),
    )
    clusters = NaturalKeyOrPKMultipleChoiceFilter(
        queryset=Cluster.objects.all(),
        to_field_name="name",
        label=_("Clusters (name or ID)"),
    )
    has_clusters = RelatedMembershipBooleanFilter(
        field_name="clusters",
        label=_("Has clusters"),
    )
    devices = NaturalKeyOrPKMultipleChoiceFilter(
        queryset=Device.objects.all(),
        to_field_name="name",
        label=_("Devices (name or ID)"),
    )
    has_devices = RelatedMembershipBooleanFilter(
        field_name="devices",
        label=_("Has devices"),
    )
    ip_addresses = django_filters.ModelMultipleChoiceFilter(
        queryset=IPAddress.objects.all(),
        label=_("IP addresses (ID)"),
    )
    has_ip_addresses = RelatedMembershipBooleanFilter(
        field_name="ip_addresses",
        label=_("Has IP addresses"),
    )
    locations = TreeNodeMultipleChoiceFilter(
        prefers_id=True,
        queryset=Location.objects.all(),
        to_field_name="name",
        label=_("Locations (names and/or IDs)"),
    )
    has_locations = RelatedMembershipBooleanFilter(
        field_name="locations",
        label=_("Has locations"),
    )
    prefixes = PrefixFilter()
    has_prefixes = RelatedMembershipBooleanFilter(
        field_name="prefixes",
        label=_("Has prefixes"),
    )
    rack_reservations = django_filters.ModelMultipleChoiceFilter(
        queryset=RackReservation.objects.all(),
        label=_("Rack reservations (ID)"),
    )
    has_rack_reservations = RelatedMembershipBooleanFilter(
        field_name="rack_reservations",
        label=_("Has rack reservations"),
    )
    racks = NaturalKeyOrPKMultipleChoiceFilter(
        queryset=Rack.objects.all(),
        to_field_name="name",
        label=_("Racks (name or ID)"),
    )
    has_racks = RelatedMembershipBooleanFilter(
        field_name="racks",
        label=_("Has racks"),
    )
    route_targets = NaturalKeyOrPKMultipleChoiceFilter(
        queryset=RouteTarget.objects.all(),
        to_field_name="name",
        label=_("Route targets (name or ID)"),
    )
    has_route_targets = RelatedMembershipBooleanFilter(
        field_name="route_targets",
        label=_("Has route targets"),
    )
    virtual_machines = NaturalKeyOrPKMultipleChoiceFilter(
        queryset=VirtualMachine.objects.all(),
        to_field_name="name",
        label=_("Virtual machines (name or ID)"),
    )
    has_virtual_machines = RelatedMembershipBooleanFilter(
        field_name="virtual_machines",
        label=_("Has virtual machines"),
    )
    vlans = django_filters.ModelMultipleChoiceFilter(
        queryset=VLAN.objects.all(),
        label=_("VLANs (ID)"),
    )
    has_vlans = RelatedMembershipBooleanFilter(
        field_name="vlans",
        label=_("Has VLANs"),
    )
    vrfs = NaturalKeyOrPKMultipleChoiceFilter(
        queryset=VRF.objects.all(),
        to_field_name="name",
        label=_("VRFs (name or ID)"),
    )
    has_vrfs = RelatedMembershipBooleanFilter(
        field_name="vrfs",
        label=_("Has VRFs"),
    )

    class Meta:
        model = Tenant
        fields = [
            "comments",
            "description",
            "id",
            "name",
            "tags",
        ]
