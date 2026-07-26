from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext, gettext_lazy as _

from nautobot.apps.constants import CHARFIELD_MAX_LENGTH
from nautobot.apps.models import BaseModel, extras_features, JSONArrayField, PrimaryModel, StatusField
from nautobot.extras.models import RoleField
from nautobot.vpn import choices


@extras_features(
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "webhooks",
)
class VPNProfile(PrimaryModel):  # pylint: disable=too-many-ancestors
    """VPNProfile model."""

    vpn_phase1_policies = models.ManyToManyField(
        to="vpn.VPNPhase1Policy",
        related_name="vpn_profiles",
        verbose_name=_("VPN Phase 1 Policy"),
        through="vpn.VPNProfilePhase1PolicyAssignment",
        blank=True,
        help_text=_("Phase 1 Policy"),
    )
    vpn_phase2_policies = models.ManyToManyField(
        to="vpn.VPNPhase2Policy",
        related_name="vpn_profiles",
        verbose_name=_("VPN Phase 2 Policy"),
        through="vpn.VPNProfilePhase2PolicyAssignment",
        blank=True,
        help_text=_("Phase 2 Policy"),
    )
    name = models.CharField(max_length=CHARFIELD_MAX_LENGTH, unique=True, verbose_name=_("name"))
    description = models.CharField(max_length=CHARFIELD_MAX_LENGTH, blank=True, verbose_name=_("description"))
    role = RoleField(blank=True, null=True, verbose_name=_("role"))
    secrets_group = models.ForeignKey(
        to="extras.SecretsGroup",
        on_delete=models.SET_NULL,
        related_name="vpn_profiles",
        default=None,
        blank=True,
        null=True,
        verbose_name=_("secrets group"),
    )
    keepalive_enabled = models.BooleanField(default=False, verbose_name=_("Enable keepalive"))
    keepalive_interval = models.PositiveIntegerField(blank=True, null=True, verbose_name=_("keepalive interval"))
    keepalive_retries = models.PositiveIntegerField(blank=True, null=True, verbose_name=_("keepalive retries"))
    nat_traversal = models.BooleanField(default=False, verbose_name=_("Enable NAT Traversal"))
    extra_options = models.JSONField(
        blank=True,
        null=True,
        help_text=_("Additional options specific to the VPN technology and/or implementation"),
        verbose_name=_("extra options"),
    )

    tenant = models.ForeignKey(
        to="tenancy.Tenant",
        on_delete=models.SET_NULL,
        related_name="vpn_profiles",
        blank=True,
        null=True,
        verbose_name=_("tenant"),
    )

    clone_fields = [
        "description",
        "role",
        "secrets_group",
        "keepalive_enabled",
        "keepalive_interval",
        "keepalive_retries",
        "nat_traversal",
        "extra_options",
    ]

    class Meta:
        """Meta class for VPNProfile."""

        ordering = ("name",)
        verbose_name = _("VPN Profile")

    def __str__(self):
        """Stringify instance."""
        return self.name


@extras_features(
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "webhooks",
)
class VPNPhase1Policy(PrimaryModel):  # pylint: disable=too-many-ancestors
    """VPNPhase1Policy model."""

    name = models.CharField(max_length=CHARFIELD_MAX_LENGTH, unique=True, verbose_name=_("name"))
    description = models.CharField(max_length=CHARFIELD_MAX_LENGTH, blank=True, verbose_name=_("description"))
    ike_version = models.CharField(
        max_length=CHARFIELD_MAX_LENGTH, choices=choices.IkeVersionChoices, blank=True, verbose_name=_("IKE version")
    )
    aggressive_mode = models.BooleanField(
        default=False, help_text=_("Only applicable to IKEv1"), verbose_name=_("aggressive mode")
    )
    encryption_algorithm = JSONArrayField(
        base_field=models.CharField(choices=choices.EncryptionAlgorithmChoices),
        blank=True,
        null=True,
        verbose_name=_("encryption algorithm"),
    )
    integrity_algorithm = JSONArrayField(
        base_field=models.CharField(choices=choices.IntegrityAlgorithmChoices),
        blank=True,
        null=True,
        verbose_name=_("integrity algorithm"),
    )
    dh_group = JSONArrayField(
        base_field=models.CharField(choices=choices.DhGroupChoices),
        blank=True,
        null=True,
        verbose_name=_("Diffie-Hellman group"),
    )
    lifetime_seconds = models.PositiveIntegerField(blank=True, null=True, verbose_name=_("Lifetime (seconds)"))
    lifetime_kb = models.PositiveIntegerField(blank=True, null=True, verbose_name=_("Lifetime (kilobytes)"))
    authentication_method = models.CharField(
        max_length=CHARFIELD_MAX_LENGTH,
        choices=choices.AuthenticationMethodChoices,
        blank=True,
        help_text=_("PSK, RSA, ECDSA, Certificate"),
        verbose_name=_("authentication method"),
    )
    tenant = models.ForeignKey(
        to="tenancy.Tenant",
        on_delete=models.SET_NULL,
        related_name="vpn_phase_1_policies",
        blank=True,
        null=True,
        verbose_name=_("tenant"),
    )

    clone_fields = [
        "description",
        "ike_version",
        "aggressive_mode",
        "encryption_algorithm",
        "integrity_algorithm",
        "dh_group",
        "lifetime_seconds",
        "lifetime_kb",
        "authentication_method",
    ]

    class Meta:
        """Meta class for VPNPhase1Policy."""

        ordering = ("name",)
        verbose_name = _("VPN Phase 1 Policy")
        verbose_name_plural = _("VPN Phase 1 Policies")

    def __str__(self):
        """Stringify instance."""
        return self.name


@extras_features(
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "webhooks",
)
class VPNPhase2Policy(PrimaryModel):  # pylint: disable=too-many-ancestors
    """VPNPhase2Policy model."""

    name = models.CharField(max_length=CHARFIELD_MAX_LENGTH, unique=True, verbose_name=_("name"))
    description = models.CharField(max_length=CHARFIELD_MAX_LENGTH, blank=True, verbose_name=_("description"))
    encryption_algorithm = JSONArrayField(
        base_field=models.CharField(choices=choices.EncryptionAlgorithmChoices),
        blank=True,
        null=True,
        verbose_name=_("encryption algorithm"),
    )
    integrity_algorithm = JSONArrayField(
        base_field=models.CharField(choices=choices.IntegrityAlgorithmChoices),
        blank=True,
        null=True,
        verbose_name=_("integrity algorithm"),
    )
    pfs_group = JSONArrayField(
        base_field=models.CharField(choices=choices.DhGroupChoices),
        blank=True,
        null=True,
        verbose_name=_("PFS group"),
    )
    lifetime = models.PositiveIntegerField(blank=True, null=True, verbose_name=_("Lifetime (seconds)"))
    tenant = models.ForeignKey(
        to="tenancy.Tenant",
        on_delete=models.SET_NULL,
        related_name="vpn_phase_2_policies",
        blank=True,
        null=True,
        verbose_name=_("tenant"),
    )

    clone_fields = [
        "description",
        "encryption_algorithm",
        "integrity_algorithm",
        "pfs_group",
        "lifetime",
    ]

    class Meta:
        """Meta class for VPNPhase2Policy."""

        ordering = ("name",)
        verbose_name = _("VPN Phase 2 Policy")
        verbose_name_plural = _("VPN Phase 2 Policies")

    def __str__(self):
        """Stringify instance."""
        return self.name


@extras_features("graphql")
class VPNProfilePhase1PolicyAssignment(BaseModel):
    vpn_profile = models.ForeignKey(
        "vpn.VPNProfile",
        on_delete=models.CASCADE,
        related_name="vpn_profile_phase1_policy_assignments",
        verbose_name=_("vpn profile"),
    )
    vpn_phase1_policy = models.ForeignKey(
        "vpn.VPNPhase1Policy",
        on_delete=models.CASCADE,
        related_name="vpn_profile_phase1_policy_assignments",
        verbose_name=_("vpn phase1 policy"),
    )
    weight = models.PositiveIntegerField(
        default=100, help_text=_("Higher weights appear later in the list"), verbose_name=_("weight")
    )
    is_metadata_associable_model = False
    documentation_static_path = "docs/user-guide/core-data-model/vpn/vpnprofile.html"

    class Meta:
        unique_together = ["vpn_profile", "vpn_phase1_policy"]
        ordering = ["weight", "vpn_profile", "vpn_phase1_policy"]

    def __str__(self):
        return f"{self.vpn_profile}: {self.vpn_phase1_policy}"


@extras_features("graphql")
class VPNProfilePhase2PolicyAssignment(BaseModel):
    vpn_profile = models.ForeignKey(
        "vpn.VPNProfile",
        on_delete=models.CASCADE,
        related_name="vpn_profile_phase2_policy_assignments",
        verbose_name=_("vpn profile"),
    )
    vpn_phase2_policy = models.ForeignKey(
        "vpn.VPNPhase2Policy",
        on_delete=models.CASCADE,
        related_name="vpn_profile_phase2_policy_assignments",
        verbose_name=_("vpn phase2 policy"),
    )
    weight = models.PositiveIntegerField(
        default=100, help_text=_("Higher weights appear later in the list"), verbose_name=_("weight")
    )
    is_metadata_associable_model = False
    documentation_static_path = "docs/user-guide/core-data-model/vpn/vpnprofile.html"

    class Meta:
        unique_together = ["vpn_profile", "vpn_phase2_policy"]
        ordering = ["weight", "vpn_profile", "vpn_phase2_policy"]

    def __str__(self):
        return f"{self.vpn_profile}: {self.vpn_phase2_policy}"


@extras_features(
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "statuses",
    "webhooks",
)
class VPN(PrimaryModel):  # pylint: disable=too-many-ancestors
    """VPN model."""

    name = models.CharField(max_length=CHARFIELD_MAX_LENGTH, unique=True, verbose_name=_("name"))
    description = models.CharField(max_length=CHARFIELD_MAX_LENGTH, blank=True, verbose_name=_("description"))
    vpn_id = models.CharField(max_length=CHARFIELD_MAX_LENGTH, blank=True, verbose_name=_("Identifier"))
    vpn_profile = models.ForeignKey(
        to="vpn.VPNProfile",
        on_delete=models.PROTECT,
        related_name="vpns",
        default=None,
        blank=True,
        null=True,
        verbose_name=_("VPN Profile"),
    )
    role = RoleField(blank=True, null=True, verbose_name=_("role"))
    tenant = models.ForeignKey(
        to="tenancy.Tenant",
        on_delete=models.SET_NULL,
        related_name="vpns",
        blank=True,
        null=True,
        verbose_name=_("tenant"),
    )
    service_type = models.CharField(
        max_length=CHARFIELD_MAX_LENGTH,
        choices=choices.VPNServiceTypeChoices,
        blank=True,
        help_text=_("Optional classification of this VPN service, for example IPSec or VXLAN-EVPN."),
        verbose_name=_("service type"),
    )
    # Nullable to support backwards-compatible migration of pre-existing VPN rows.
    status = StatusField(blank=True, null=True, verbose_name=_("status"))
    extra_attributes = models.JSONField(
        blank=True,
        default=dict,
        help_text=_("Free-form scalar service metadata only; not for references to real Nautobot objects."),
        verbose_name=_("extra attributes"),
    )

    clone_fields = [
        "description",
        "vpn_id",
        "vpn_profile",
        "role",
        "tenant",
        "service_type",
        "status",
        "extra_attributes",
    ]

    class Meta:
        """Meta class for VPN."""

        ordering = ("name",)
        verbose_name = _("VPN")

    def __str__(self):
        """Stringify instance."""
        return self.name

    @property
    def can_add_termination(self):
        """P2P VPN services are limited to two terminations."""
        if self.service_type in choices.VPNServiceTypeChoices.P2P:
            return self.vpn_terminations.count() < 2
        return True

    def clean(self):
        super().clean()

        if self.service_type in choices.VPNServiceTypeChoices.VXLAN_TYPES:
            if not self.vpn_id:
                raise ValidationError({"vpn_id": _("Identifier is required for VXLAN-based VPN services.")})

            try:
                vni = int(self.vpn_id)
            except (TypeError, ValueError) as exc:
                raise ValidationError(
                    {"vpn_id": _("Identifier must be a numeric VNI for VXLAN-based VPN services.")}
                ) from exc

            if not (choices.VPNServiceTypeChoices.VXLAN_VNI_MIN <= vni <= choices.VPNServiceTypeChoices.VXLAN_VNI_MAX):
                raise ValidationError(
                    {
                        "vpn_id": (
                            gettext("VNI must be between %(VXLAN_VNI_MIN)s and %(VXLAN_VNI_MAX)s.")
                            % {
                                "VXLAN_VNI_MIN": choices.VPNServiceTypeChoices.VXLAN_VNI_MIN,
                                "VXLAN_VNI_MAX": choices.VPNServiceTypeChoices.VXLAN_VNI_MAX,
                            }
                        )
                    }
                )


@extras_features(
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "statuses",
    "webhooks",
)
class VPNTunnel(PrimaryModel):  # pylint: disable=too-many-ancestors
    """VPNTunnel model."""

    name = models.CharField(max_length=CHARFIELD_MAX_LENGTH, unique=True, verbose_name=_("name"))
    description = models.CharField(max_length=CHARFIELD_MAX_LENGTH, blank=True, verbose_name=_("description"))
    tunnel_id = models.CharField(max_length=CHARFIELD_MAX_LENGTH, blank=True, verbose_name=_("Tunnel ID"))
    vpn_profile = models.ForeignKey(
        to="vpn.VPNProfile",
        on_delete=models.PROTECT,
        related_name="vpn_tunnels",
        blank=True,
        null=True,
        verbose_name=_("VPN Profile"),
    )
    vpn = models.ForeignKey(
        to="vpn.VPN",
        on_delete=models.CASCADE,
        related_name="vpn_tunnels",
        blank=True,
        null=True,
        verbose_name=_("VPN"),
        help_text=_("VPN to which this tunnel belongs"),
    )
    role = RoleField(blank=True, null=True, verbose_name=_("role"))
    status = StatusField(blank=False, null=False, verbose_name=_("status"))
    secrets_group = models.ForeignKey(
        to="extras.SecretsGroup",
        on_delete=models.SET_NULL,
        related_name="vpn_tunnels",
        default=None,
        blank=True,
        null=True,
        verbose_name=_("secrets group"),
    )
    encapsulation = models.CharField(
        max_length=CHARFIELD_MAX_LENGTH,
        choices=choices.EncapsulationChoices,
        blank=True,
        verbose_name=_("encapsulation"),
    )
    endpoint_a = models.ForeignKey(
        to="vpn.VPNTunnelEndpoint",
        on_delete=models.SET_NULL,
        related_name="endpoint_a_vpn_tunnels",
        blank=True,
        null=True,
        verbose_name=_("Endpoint A"),
        help_text=_("Tunnel termination A"),
    )
    endpoint_z = models.ForeignKey(
        to="vpn.VPNTunnelEndpoint",
        on_delete=models.SET_NULL,
        related_name="endpoint_z_vpn_tunnels",
        blank=True,
        null=True,
        verbose_name=_("Endpoint Z"),
        help_text=_("Tunnel termination Z"),
    )
    tenant = models.ForeignKey(
        to="tenancy.Tenant",
        on_delete=models.SET_NULL,
        related_name="vpn_tunnels",
        blank=True,
        null=True,
        verbose_name=_("tenant"),
    )

    clone_fields = [
        "description",
        "vpn",
        "tunnel_id",
        "encapsulation",
        "endpoint_a",
        "endpoint_z",
        "status",
        "vpn_profile",
        "tenant",
        "role",
    ]

    class Meta:
        """Meta class for VPNTunnel."""

        ordering = ("name",)
        verbose_name = _("VPN Tunnel")

    def __str__(self):
        """Stringify instance."""
        return self.name

    def clean(self):
        super().clean()
        if self.endpoint_a and self.endpoint_z and self.endpoint_a == self.endpoint_z:
            raise ValidationError(_("Endpoint A and Endpoint Z cannot be the same."))


@extras_features(
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "webhooks",
)
class VPNTunnelEndpoint(PrimaryModel):  # pylint: disable=too-many-ancestors
    """VPNTunnelEndpoint model."""

    name = models.CharField(max_length=CHARFIELD_MAX_LENGTH, editable=False)
    device = models.ForeignKey(
        to="dcim.Device",
        on_delete=models.CASCADE,
        related_name="vpn_tunnel_endpoints",
        blank=True,
        null=True,
        verbose_name=_("Device"),
    )
    source_interface = models.OneToOneField(
        to="dcim.Interface",
        on_delete=models.CASCADE,
        related_name="vpn_tunnel_endpoints_src_int",
        blank=True,
        null=True,
        verbose_name=_("Source Interface"),
    )
    source_ipaddress = models.ForeignKey(
        to="ipam.IPAddress",
        on_delete=models.SET_NULL,
        related_name="vpn_tunnel_endpoints_src_ip",
        blank=True,
        null=True,
        verbose_name=_("Source IP Address"),
        help_text=_("Mutually Exclusive with Source FQDN."),
    )
    source_fqdn = models.CharField(
        max_length=CHARFIELD_MAX_LENGTH,
        blank=True,
        verbose_name=_("Source FQDN"),
        help_text=_("Mutually Exclusive with Source IP Address"),
    )
    tunnel_interface = models.OneToOneField(
        to="dcim.Interface",
        on_delete=models.SET_NULL,
        related_name="vpn_tunnel_endpoints_tunnel",
        blank=True,
        null=True,
        verbose_name=_("Tunnel Interface"),
    )
    vpn_profile = models.ForeignKey(
        to="vpn.VPNProfile",
        on_delete=models.PROTECT,
        related_name="vpn_tunnel_endpoints",
        blank=True,
        null=True,
        verbose_name=_("VPN Profile"),
    )
    role = RoleField(blank=True, null=True, verbose_name=_("role"))
    protected_prefixes = models.ManyToManyField(
        to="ipam.Prefix",
        related_name="vpn_tunnel_endpoints",
        blank=True,
        verbose_name=_("Protected Prefixes"),
    )
    protected_prefixes_dg = models.ManyToManyField(
        to="extras.DynamicGroup",
        related_name="vpn_tunnel_endpoints",
        blank=True,
        verbose_name=_("Protected Prefixes Dynamic Group"),
    )
    tenant = models.ForeignKey(
        to="tenancy.Tenant",
        on_delete=models.SET_NULL,
        related_name="vpn_tunnel_endpoints",
        blank=True,
        null=True,
        verbose_name=_("tenant"),
    )

    clone_fields = [
        "vpn_profile",
        "device",
        "source_interface",
        "source_ipaddress",
        "source_fqdn",
        "protected_prefixes",
        "protected_prefixes_dg",
    ]

    natural_key_field_names = ["pk"]  # TODO: name is not unique, nor are there any uniqueness criteria on this model?

    class Meta:
        """Meta class for VPNTunnelEndpoint."""

        ordering = ("name",)
        verbose_name = _("VPN Tunnel Endpoint")

    def _name(self):
        """Dynamic name field."""
        if self.source_interface:
            parent_intf = f"{self.source_interface.parent.name} {self.source_interface.name}"
            if self.source_ipaddress:
                return f"{parent_intf} ({self.source_ipaddress.address})"
            return parent_intf
        return self.source_fqdn

    def __str__(self):
        """Stringify instance."""
        return self.name

    def clean(self):
        super().clean()
        if self.source_ipaddress and self.source_fqdn:
            raise ValidationError(
                _("Source IP Address and Source FQDN are mutually exclusive fields. Select only one.")
            )
        if not any([self.source_interface, self.source_ipaddress, self.source_fqdn]):
            raise ValidationError(_("Source Interface or Source IP Address or Source FQDN Is required."))
        if self.source_interface and not self.source_interface.parent:
            raise ValidationError(_("Source Interface must belong to a device."))
        if (
            self.source_ipaddress
            and self.source_interface
            and (self.source_ipaddress not in self.source_interface.ip_addresses.all())
        ):
            raise ValidationError(_("Source IP address must be assigned to Source Interface."))
        if (
            self.tunnel_interface
            and self.source_interface
            and (self.tunnel_interface not in self.source_interface.parent.all_interfaces)
        ):
            raise ValidationError(_("Tunnel Interface and Source Interface must be on the same device"))

    def save(self, *args, **kwargs):
        if self.source_interface:
            self.device = self.source_interface.parent
        self.name = self._name()
        super().save(*args, **kwargs)


@extras_features(
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "webhooks",
)
class VPNTermination(PrimaryModel):
    """Bind a VPN service to exactly one VLAN, Interface, or VMInterface."""

    natural_key_field_names = ["pk"]

    vpn = models.ForeignKey(
        to="vpn.VPN", on_delete=models.CASCADE, related_name="vpn_terminations", verbose_name=_("vpn")
    )
    vlan = models.ForeignKey(
        to="ipam.VLAN",
        on_delete=models.CASCADE,
        related_name="vpn_terminations",
        blank=True,
        null=True,
        verbose_name=_("vlan"),
    )
    interface = models.ForeignKey(
        to="dcim.Interface",
        on_delete=models.CASCADE,
        related_name="vpn_terminations",
        blank=True,
        null=True,
        verbose_name=_("interface"),
    )
    vm_interface = models.ForeignKey(
        to="virtualization.VMInterface",
        on_delete=models.CASCADE,
        related_name="vpn_terminations",
        blank=True,
        null=True,
        verbose_name=_("vm interface"),
    )

    clone_fields = ["vpn"]

    class Meta:
        ordering = ("vpn__name",)
        verbose_name = _("VPN Termination")
        verbose_name_plural = _("VPN Terminations")
        constraints = [
            models.UniqueConstraint(
                fields=["vlan"],
                name="vpn_vpntermination_unique_vlan",
            ),
            models.UniqueConstraint(
                fields=["interface"],
                name="vpn_vpntermination_unique_interface",
            ),
            models.UniqueConstraint(
                fields=["vm_interface"],
                name="vpn_vpntermination_unique_vm_interface",
            ),
        ]

    def __str__(self):
        if self.pk and self.assigned_object:
            return f"{self.assigned_object} <> {self.vpn}"
        return super().__str__()

    @property
    def assigned_object(self):
        return self.vlan or self.interface or self.vm_interface

    @property
    def assigned_object_type(self):
        if self.vlan:
            return "ipam.vlan"
        if self.interface:
            return "dcim.interface"
        if self.vm_interface:
            return "virtualization.vminterface"
        return None

    @property
    def assigned_object_parent(self):
        if self.interface:
            return self.interface.device
        if self.vm_interface:
            return self.vm_interface.virtual_machine
        if self.vlan:
            return self.vlan.vlan_group
        return None

    def clean(self):
        super().clean()

        selected = [obj for obj in (self.vlan, self.interface, self.vm_interface) if obj is not None]
        if len(selected) != 1:
            raise ValidationError(_("Exactly one of vlan, interface, or vm_interface must be set."))

        duplicate_fields = {
            "vlan": self.vlan,
            "interface": self.interface,
            "vm_interface": self.vm_interface,
        }
        for field_name, value in duplicate_fields.items():
            if value is None:
                continue
            if self.__class__.objects.exclude(pk=self.pk).filter(**{field_name: value}).exists():
                raise ValidationError({field_name: _("This object is already assigned to another VPN termination.")})

        if self.vpn_id is None:
            return

        if self.vpn.service_type in choices.VPNServiceTypeChoices.P2P:
            count = self.vpn.vpn_terminations.exclude(pk=self.pk).count()
            if count >= 2:
                raise ValidationError(
                    gettext("%(get_service_type_display)s VPNs cannot have more than 2 terminations.")
                    % {"get_service_type_display": self.vpn.get_service_type_display()}
                )
