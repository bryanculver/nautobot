"""Forms for the vpn models."""

import logging

from django import forms
from django.utils.translation import gettext_lazy as _

from nautobot.apps.forms import (
    add_blank_choice,
    APISelect,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    JSONArrayFormField,
    NautobotBulkEditForm,
    NautobotFilterForm,
    NautobotModelForm,
    RoleModelBulkEditFormMixin,
    RoleModelFilterFormMixin,
    StaticSelect2,
    StaticSelect2Multiple,
    StatusModelBulkEditFormMixin,
    StatusModelFilterFormMixin,
    TagFilterField,
    TagsBulkEditFormMixin,
)
from nautobot.core.forms.constants import BOOLEAN_WITH_BLANK_CHOICES
from nautobot.dcim.choices import InterfaceTypeChoices
from nautobot.dcim.models import Device, Interface
from nautobot.extras.models import DynamicGroup, SecretsGroup, Status
from nautobot.ipam.models import IPAddress, Prefix, VLAN
from nautobot.tenancy.forms import TenancyFilterForm, TenancyForm
from nautobot.tenancy.models import Tenant
from nautobot.virtualization.models import VMInterface

from . import choices, models

logger = logging.getLogger(__name__)


class VPNProfileForm(NautobotModelForm, TenancyForm):  # pylint: disable=too-many-ancestors
    """Form for creating and updating VPNProfile."""

    secrets_group = DynamicModelChoiceField(
        queryset=SecretsGroup.objects.all(),
        required=False,
        label=_("Secrets Group"),
        help_text=_("Secrets Group for the VPN Profile."),
    )

    class Meta:
        """Meta attributes."""

        model = models.VPNProfile
        fields = [
            "name",
            "description",
            "keepalive_interval",
            "keepalive_retries",
            "keepalive_enabled",
            "secrets_group",
            "role",
            "extra_options",
            "nat_traversal",
            "tenant_group",
            "tenant",
            "tags",
        ]


class VPNProfileBulkEditForm(RoleModelBulkEditFormMixin, TagsBulkEditFormMixin, NautobotBulkEditForm):  # pylint: disable=too-many-ancestors
    """VPNProfile bulk edit form."""

    pk = forms.ModelMultipleChoiceField(queryset=models.VPNProfile.objects.all(), widget=forms.MultipleHiddenInput)
    description = forms.CharField(required=False, label=_("Description"))
    keepalive_interval = forms.IntegerField(min_value=0, required=False, label=_("Keepalive Interval (seconds)"))
    keepalive_retries = forms.IntegerField(min_value=0, required=False, label=_("Keepalive Retries"))
    keepalive_enabled = forms.NullBooleanField(
        required=False, widget=StaticSelect2(choices=BOOLEAN_WITH_BLANK_CHOICES), label=_("Keepalive Enabled")
    )
    nat_traversal = forms.NullBooleanField(
        required=False, widget=StaticSelect2(choices=BOOLEAN_WITH_BLANK_CHOICES), label=_("NAT Traversal")
    )
    tenant = DynamicModelChoiceField(
        required=False,
        queryset=Tenant.objects.all(),
        label=_("Tenant"),
    )

    class Meta:
        """Meta attributes."""

        model = models.VPNProfile
        nullable_fields = [
            "description",
            "keepalive_interval",
            "keepalive_retries",
        ]


VPNProfilePh1FormSet = forms.inlineformset_factory(
    parent_model=models.VPNProfile,
    model=models.VPNProfilePhase1PolicyAssignment,
    fields=("vpn_phase1_policy", "weight"),
    extra=1,
    widgets={
        "vpn_phase1_policy": APISelect(api_url="/api/vpn/vpn-phase-1-policies/"),
        "weight": forms.NumberInput(attrs={"class": "form-control"}),
    },
)


VPNProfilePh2FormSet = forms.inlineformset_factory(
    parent_model=models.VPNProfile,
    model=models.VPNProfilePhase2PolicyAssignment,
    fields=("vpn_phase2_policy", "weight"),
    extra=1,
    widgets={
        "vpn_phase2_policy": APISelect(api_url="/api/vpn/vpn-phase-2-policies/"),
        "weight": forms.NumberInput(attrs={"class": "form-control"}),
    },
)


class VPNProfileFilterForm(NautobotFilterForm, RoleModelFilterFormMixin, TenancyFilterForm):  # pylint: disable=too-many-ancestors
    """Filter form for VPNProfile."""

    model = models.VPNProfile

    q = forms.CharField(required=False, label=_("Search"))
    vpn_phase1_policies = DynamicModelMultipleChoiceField(
        required=False,
        queryset=models.VPNPhase1Policy.objects.all(),
        label=_("Phase 1 Policies"),
    )
    vpn_phase2_policies = DynamicModelMultipleChoiceField(
        required=False,
        queryset=models.VPNPhase2Policy.objects.all(),
        label=_("Phase 2 Policies"),
    )
    keepalive_enabled = forms.NullBooleanField(
        required=False,
        widget=StaticSelect2(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label=_("Keepalive Enabled"),
    )
    nat_traversal = forms.NullBooleanField(
        required=False,
        widget=StaticSelect2(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label=_("NAT Traversal Enabled"),
    )
    secrets_group = DynamicModelMultipleChoiceField(
        required=False,
        queryset=SecretsGroup.objects.all(),
        label=_("Secrets Group"),
    )
    tags = TagFilterField(model)

    field_order = [
        "vpn_phase1_policies",
        "vpn_phase2_policies",
        "keepalive_enabled",
        "nat_traversal",
        "role",
        "secrets_group",
        "tenant",
        "tenant_group",
        "tags",
    ]


class VPNPhase1PolicyForm(NautobotModelForm, TenancyForm):  # pylint: disable=too-many-ancestors
    """Form for creating and updating VPNPhase1Policy."""

    ike_version = forms.ChoiceField(
        required=False,
        choices=add_blank_choice(choices.IkeVersionChoices),
        widget=StaticSelect2,
        label=_("IKE Version"),
    )
    authentication_method = forms.ChoiceField(
        required=False,
        choices=add_blank_choice(choices.AuthenticationMethodChoices),
        widget=StaticSelect2,
        label=_("Authentication Method"),
    )

    class Meta:
        """Meta attributes."""

        model = models.VPNPhase1Policy
        fields = "__all__"


class VPNPhase1PolicyBulkEditForm(TagsBulkEditFormMixin, NautobotBulkEditForm):  # pylint: disable=too-many-ancestors
    """VPNPhase1Policy bulk edit form."""

    pk = forms.ModelMultipleChoiceField(queryset=models.VPNPhase1Policy.objects.all(), widget=forms.MultipleHiddenInput)
    description = forms.CharField(required=False, label=_("Description"))
    ike_version = forms.ChoiceField(
        required=False,
        choices=add_blank_choice(choices.IkeVersionChoices),
        widget=StaticSelect2,
        label=_("Ike Version"),
    )
    aggressive_mode = forms.NullBooleanField(
        required=False, widget=StaticSelect2(choices=BOOLEAN_WITH_BLANK_CHOICES), label=_("Aggressive Mode")
    )
    encryption_algorithm = JSONArrayFormField(
        choices=choices.EncryptionAlgorithmChoices,
        base_field=forms.CharField(),
        required=False,
        label=_("Encryption Algorithm"),
    )
    integrity_algorithm = JSONArrayFormField(
        choices=choices.IntegrityAlgorithmChoices,
        base_field=forms.CharField(),
        required=False,
        label=_("Integrity Algorithm"),
    )
    dh_group = JSONArrayFormField(
        choices=choices.DhGroupChoices,
        base_field=forms.CharField(),
        required=False,
        label=_("Dh Group"),
    )
    lifetime_seconds = forms.IntegerField(
        min_value=0,
        required=False,
    )
    lifetime_kb = forms.IntegerField(
        min_value=0,
        required=False,
    )
    authentication_method = forms.ChoiceField(
        required=False,
        choices=add_blank_choice(choices.AuthenticationMethodChoices),
        widget=StaticSelect2,
        label=_("Authentication Method"),
    )

    class Meta:
        """Meta attributes."""

        model = models.VPNPhase1Policy
        nullable_fields = [
            "description",
            "ike_version",
            "encryption_algorithm",
            "integrity_algorithm",
            "dh_group",
            "lifetime_seconds",
            "lifetime_kb",
            "authentication_method",
        ]


class VPNPhase1PolicyFilterForm(NautobotFilterForm, TenancyFilterForm):  # pylint: disable=too-many-ancestors
    """Filter form for VPNPhase1Policy."""

    model = models.VPNPhase1Policy

    q = forms.CharField(required=False, label=_("Search"))
    ike_version = forms.ChoiceField(
        required=False,
        initial=choices.IkeVersionChoices.ike_v2,
        choices=choices.IkeVersionChoices.CHOICES,
        widget=StaticSelect2,
        label=_("IKE Version"),
    )
    aggressive_mode = forms.NullBooleanField(
        required=False,
        widget=StaticSelect2(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label=_("IKEv1 Aggressive Mode Enabled"),
    )
    encryption_algorithm = forms.MultipleChoiceField(
        required=False,
        choices=choices.EncryptionAlgorithmChoices.CHOICES,
        widget=StaticSelect2Multiple(),
        label=_("Encryption Algorithm"),
    )
    integrity_algorithm = forms.MultipleChoiceField(
        required=False,
        choices=choices.IntegrityAlgorithmChoices.CHOICES,
        widget=StaticSelect2Multiple(),
        label=_("Integrity Algorithm"),
    )
    dh_group = forms.MultipleChoiceField(
        required=False,
        choices=choices.DhGroupChoices.CHOICES,
        widget=StaticSelect2Multiple(),
        label=_("Diffie-Hellman Group"),
    )
    authentication_method = forms.MultipleChoiceField(
        required=False,
        choices=choices.AuthenticationMethodChoices.CHOICES,
        widget=StaticSelect2Multiple(),
        label=_("Authentication Method"),
    )
    tags = TagFilterField(model)

    field_order = [
        "ike_version",
        "aggressive_mode",
        "encryption_algorithm",
        "integrity_algorithm",
        "dh_group",
        "authentication_method",
        "tenant",
        "tenant_group",
        "tags",
    ]


class VPNPhase2PolicyForm(NautobotModelForm, TenancyForm):  # pylint: disable=too-many-ancestors
    """Form for creating and updating VPNPhase2Policy."""

    class Meta:
        """Meta attributes."""

        model = models.VPNPhase2Policy
        fields = "__all__"


class VPNPhase2PolicyBulkEditForm(TagsBulkEditFormMixin, NautobotBulkEditForm):  # pylint: disable=too-many-ancestors
    """VPNPhase2Policy bulk edit form."""

    pk = forms.ModelMultipleChoiceField(queryset=models.VPNPhase2Policy.objects.all(), widget=forms.MultipleHiddenInput)
    description = forms.CharField(required=False, label=_("Description"))
    encryption_algorithm = JSONArrayFormField(
        choices=choices.EncryptionAlgorithmChoices,
        base_field=forms.CharField(),
        required=False,
        label=_("Encryption Algorithm"),
    )
    integrity_algorithm = JSONArrayFormField(
        choices=choices.IntegrityAlgorithmChoices,
        base_field=forms.CharField(),
        required=False,
        label=_("Integrity Algorithm"),
    )
    pfs_group = JSONArrayFormField(
        choices=choices.DhGroupChoices,
        base_field=forms.CharField(),
        required=False,
        label=_("Pfs Group"),
    )
    lifetime = forms.IntegerField(
        min_value=0,
        required=False,
    )

    class Meta:
        """Meta attributes."""

        model = models.VPNPhase2Policy
        nullable_fields = [
            "description",
            "encryption_algorithm",
            "integrity_algorithm",
            "pfs_group",
            "lifetime",
        ]


class VPNPhase2PolicyFilterForm(NautobotFilterForm, TenancyFilterForm):  # pylint: disable=too-many-ancestors
    """Filter form for VPNPhase2Policy."""

    model = models.VPNPhase2Policy

    q = forms.CharField(required=False, label=_("Search"))
    encryption_algorithm = forms.MultipleChoiceField(
        required=False,
        choices=choices.EncryptionAlgorithmChoices.CHOICES,
        widget=StaticSelect2Multiple(),
        label=_("Encryption Algorithm"),
    )
    integrity_algorithm = forms.MultipleChoiceField(
        required=False,
        choices=choices.IntegrityAlgorithmChoices.CHOICES,
        widget=StaticSelect2Multiple(),
        label=_("Integrity Algorithm"),
    )
    pfs_group = forms.MultipleChoiceField(
        required=False,
        choices=choices.DhGroupChoices.CHOICES,
        widget=StaticSelect2Multiple(),
        label=_("PFS Group"),
    )
    tags = TagFilterField(model)

    field_order = [
        "encryption_algorithm",
        "integrity_algorithm",
        "pfs_group",
        "tenant",
        "tenant_group",
        "tags",
    ]


class VPNForm(NautobotModelForm, TenancyForm):  # pylint: disable=too-many-ancestors
    """Form for creating and updating VPN."""

    vpn_profile = DynamicModelChoiceField(
        queryset=models.VPNProfile.objects.all(),
        required=False,
        label=_("VPN Profile"),
    )
    service_type = forms.ChoiceField(
        required=False,
        choices=add_blank_choice(choices.VPNServiceTypeChoices),
        widget=StaticSelect2,
        label=_("Service Type"),
    )
    vpn_id = forms.CharField(required=False, label=_("Identifier"))
    status = DynamicModelChoiceField(
        queryset=Status.objects.all(),
        required=False,
        query_params={"content_types": models.VPN._meta.label_lower},
    )

    class Meta:
        """Meta attributes."""

        model = models.VPN
        fields = "__all__"


class VPNBulkEditForm(
    TagsBulkEditFormMixin, StatusModelBulkEditFormMixin, RoleModelBulkEditFormMixin, NautobotBulkEditForm
):  # pylint: disable=too-many-ancestors
    """VPN bulk edit form."""

    pk = forms.ModelMultipleChoiceField(queryset=models.VPN.objects.all(), widget=forms.MultipleHiddenInput)
    description = forms.CharField(required=False, label=_("Description"))
    vpn_profile = DynamicModelChoiceField(
        queryset=models.VPNProfile.objects.all(),
        required=False,
        label=_("VPN Profile"),
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label=_("Tenant"),
    )
    service_type = forms.ChoiceField(
        required=False,
        choices=add_blank_choice(choices.VPNServiceTypeChoices),
        widget=StaticSelect2,
        label=_("Service Type"),
    )
    vpn_id = forms.CharField(required=False, label=_("Identifier"))

    class Meta:
        """Meta attributes."""

        model = models.VPN
        nullable_fields = [
            "description",
            "vpn_profile",
            "vpn_id",
            "service_type",
            "status",
        ]


class VPNFilterForm(NautobotFilterForm, RoleModelFilterFormMixin, TenancyFilterForm):  # pylint: disable=too-many-ancestors
    """Filter form for VPN."""

    model = models.VPN

    q = forms.CharField(required=False, label=_("Search"))
    vpn_profile = DynamicModelMultipleChoiceField(
        required=False,
        queryset=models.VPNProfile.objects.all(),
        label=_("VPN Profile"),
    )
    service_type = forms.MultipleChoiceField(
        choices=choices.VPNServiceTypeChoices,
        required=False,
        widget=StaticSelect2Multiple(),
    )
    vpn_id = forms.CharField(required=False, label=_("Identifier"))
    tags = TagFilterField(model)

    field_order = [
        "vpn_profile",
        "service_type",
        "role",
        "vpn_id",
        "tenant",
        "tenant_group",
        "tags",
    ]


class VPNTunnelForm(NautobotModelForm, TenancyForm):  # pylint: disable=too-many-ancestors
    """Form for creating and updating VPNTunnel."""

    vpn_profile = DynamicModelChoiceField(
        queryset=models.VPNProfile.objects.all(),
        required=False,
        label=_("VPN Profile"),
    )
    vpn = DynamicModelChoiceField(
        queryset=models.VPN.objects.all(),
        required=False,
        label=_("VPN"),
    )
    encapsulation = forms.ChoiceField(
        required=True,
        choices=add_blank_choice(choices.EncapsulationChoices),
        widget=StaticSelect2,
        label=_("Encapsulation"),
    )
    endpoint_a = DynamicModelChoiceField(
        queryset=models.VPNTunnelEndpoint.objects.all(),
        required=False,
        label=_("Endpoint A"),
    )
    endpoint_z = DynamicModelChoiceField(
        queryset=models.VPNTunnelEndpoint.objects.all(),
        required=False,
        label=_("Endpoint Z"),
    )

    class Meta:
        """Meta attributes."""

        model = models.VPNTunnel
        fields = "__all__"


class VPNTunnelBulkEditForm(RoleModelBulkEditFormMixin, TagsBulkEditFormMixin, NautobotBulkEditForm):  # pylint: disable=too-many-ancestors
    """VPNTunnel bulk edit form."""

    pk = forms.ModelMultipleChoiceField(queryset=models.VPNTunnel.objects.all(), widget=forms.MultipleHiddenInput)
    description = forms.CharField(required=False, label=_("Description"))
    vpn_profile = DynamicModelChoiceField(
        queryset=models.VPNProfile.objects.all(),
        required=False,
        label=_("VPN Profile"),
    )
    vpn = DynamicModelChoiceField(
        queryset=models.VPN.objects.all(),
        required=False,
        label=_("VPN"),
    )
    secrets_group = DynamicModelChoiceField(
        queryset=SecretsGroup.objects.all(),
        required=False,
        label=_("Secrets Group"),
    )
    encapsulation = forms.ChoiceField(
        required=False,
        choices=add_blank_choice(choices.EncapsulationChoices),
        widget=StaticSelect2,
        label=_("Encapsulation"),
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label=_("Tenant"),
    )

    class Meta:
        """Meta attributes."""

        model = models.VPNTunnel
        nullable_fields = [
            "vpn_profile",
            "vpn",
            "description",
            "encapsulation",
        ]


class VPNTunnelFilterForm(NautobotFilterForm, RoleModelFilterFormMixin, StatusModelFilterFormMixin, TenancyFilterForm):  # pylint: disable=too-many-ancestors
    """Filter form for VPNTunnel."""

    model = models.VPNTunnel

    q = forms.CharField(required=False, label=_("Search"))
    vpn = DynamicModelMultipleChoiceField(
        required=False,
        queryset=models.VPN.objects.all(),
        label=_("VPN"),
    )
    vpn_profile = DynamicModelMultipleChoiceField(
        required=False,
        queryset=models.VPNProfile.objects.all(),
        label=_("VPN Profile"),
    )
    endpoint_a = DynamicModelMultipleChoiceField(
        required=False,
        queryset=models.VPNTunnelEndpoint.objects.all(),
        label=_("Endpoint A"),
    )
    endpoint_z = DynamicModelMultipleChoiceField(
        required=False,
        queryset=models.VPNTunnelEndpoint.objects.all(),
        label=_("Endpoint Z"),
    )
    encapsulation = forms.MultipleChoiceField(
        required=False,
        choices=choices.EncapsulationChoices.CHOICES,
        label=_("Encapsulation"),
        widget=StaticSelect2Multiple(),
    )
    secrets_group = DynamicModelMultipleChoiceField(
        required=False,
        queryset=SecretsGroup.objects.all(),
        label=_("Secrets Group"),
    )
    tags = TagFilterField(model)

    field_order = [
        "vpn",
        "vpn_profile",
        "endpoint_a",
        "endpoint_z",
        "encapsulation",
        "role",
        "secrets_group",
        "status",
        "tenant",
        "tenant_group",
        "tags",
    ]


class VPNTunnelEndpointForm(NautobotModelForm, TenancyForm):  # pylint: disable=too-many-ancestors
    """Form for creating and updating VPNTunnelEndpoint."""

    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label=_("Device"),
    )
    source_interface = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        label=_("Source Interface"),
        query_params={
            "device": "$device",
        },
    )
    source_ipaddress = DynamicModelChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        label=_("Source IP Address"),
        query_params={
            "interfaces": "$source_interface",
        },
    )
    tunnel_interface = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        label=_("Tunnel Interface"),
        query_params={
            "device": "$device",
            "type": InterfaceTypeChoices.TYPE_TUNNEL,
        },
        help_text=_("Interface must be of type Tunnel"),
    )
    vpn_profile = DynamicModelChoiceField(
        queryset=models.VPNProfile.objects.all(),
        required=False,
        label=_("VPN Profile"),
        help_text=_("VPN Profile for the tunnel endpoint."),
    )
    protected_prefixes = DynamicModelMultipleChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        label=_("Protected Prefixes"),
        help_text=_("Protected Prefixes behind the tunnel endpoint."),
    )
    protected_prefixes_dg = DynamicModelMultipleChoiceField(
        queryset=DynamicGroup.objects.all(),
        required=False,
        label=_("Protected Prefixes Dynamic Group"),
        to_field_name="name",
        query_params={"content_type": "ipam.prefix"},
        help_text=_("Protected Prefixes behind the tunnel endpoint."),
    )

    class Meta:
        """Meta attributes."""

        model = models.VPNTunnelEndpoint
        fields = "__all__"


class VPNTunnelEndpointBulkEditForm(RoleModelBulkEditFormMixin, TagsBulkEditFormMixin, NautobotBulkEditForm):  # pylint: disable=too-many-ancestors
    """VPNTunnelEndpoint bulk edit form."""

    pk = forms.ModelMultipleChoiceField(
        queryset=models.VPNTunnelEndpoint.objects.all(), widget=forms.MultipleHiddenInput
    )
    vpn_profile = DynamicModelChoiceField(
        queryset=models.VPNProfile.objects.all(),
        required=False,
        label=_("VPN Profile"),
        help_text=_("VPN Profile for the tunnel endpoint."),
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label=_("Tenant"),
    )

    class Meta:
        """Meta attributes."""

        model = models.VPNTunnelEndpoint
        nullable_fields = [
            "vpn_profile",
        ]


class VPNTunnelEndpointFilterForm(NautobotFilterForm, RoleModelFilterFormMixin, TenancyFilterForm):  # pylint: disable=too-many-ancestors
    """Filter form for VPNTunnelEndpoint."""

    model = models.VPNTunnelEndpoint

    q = forms.CharField(required=False, label=_("Search"))
    vpn_profile = DynamicModelMultipleChoiceField(
        required=False,
        queryset=models.VPNProfile.objects.all(),
        label=_("VPN Profile"),
    )
    device = DynamicModelMultipleChoiceField(
        required=False,
        queryset=Device.objects.all(),
        label=_("Device"),
    )
    tags = TagFilterField(model)

    field_order = [
        "vpn_profile",
        "device",
        "role",
        "tenant",
        "tenant_group",
        "tags",
    ]


#
# VPN termination forms
#


class VPNTerminationForm(NautobotModelForm):
    """Form for creating and updating VPNTermination."""

    vpn = DynamicModelChoiceField(
        queryset=models.VPN.objects.all(),
        required=True,
        label=_("VPN"),
    )
    vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        label=_("VLAN"),
    )
    interface = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        label=_("Interface"),
    )
    vm_interface = DynamicModelChoiceField(
        queryset=VMInterface.objects.all(),
        required=False,
        label=_("VM Interface"),
    )

    class Meta:
        model = models.VPNTermination
        fields = ["vpn", "vlan", "interface", "vm_interface", "tags"]

    def clean(self):
        super().clean()
        cleaned_data = self.cleaned_data
        selected = [field for field in ("vlan", "interface", "vm_interface") if cleaned_data.get(field)]
        if len(selected) != 1:
            raise forms.ValidationError(_("Exactly one of VLAN, interface, or VM interface must be selected."))
        return cleaned_data


class VPNTerminationBulkEditForm(TagsBulkEditFormMixin, NautobotBulkEditForm):  # pylint: disable=too-many-ancestors
    """VPNTermination bulk edit form."""

    pk = forms.ModelMultipleChoiceField(queryset=models.VPNTermination.objects.all(), widget=forms.MultipleHiddenInput)
    vpn = DynamicModelChoiceField(
        queryset=models.VPN.objects.all(),
        required=False,
        label=_("VPN"),
    )

    class Meta:
        """Meta attributes."""

        model = models.VPNTermination
        nullable_fields = []


class VPNTerminationFilterForm(NautobotFilterForm):
    """Filter form for VPNTermination list view."""

    model = models.VPNTermination
    q = forms.CharField(required=False, label=_("Search"))
    vpn = DynamicModelMultipleChoiceField(
        queryset=models.VPN.objects.all(),
        required=False,
        label=_("VPN"),
    )
    vlan = DynamicModelMultipleChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        label=_("VLAN"),
    )
    interface = DynamicModelMultipleChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        label=_("Interface"),
    )
    vm_interface = DynamicModelMultipleChoiceField(
        queryset=VMInterface.objects.all(),
        required=False,
        label=_("VM Interface"),
    )
    tags = TagFilterField(model)
