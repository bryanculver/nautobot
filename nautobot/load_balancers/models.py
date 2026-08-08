"""Models for Load Balancer Models."""

from django.core.validators import MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from nautobot.core.constants import CHARFIELD_MAX_LENGTH
from nautobot.core.models import BaseModel
from nautobot.core.models.generics import PrimaryModel
from nautobot.extras.models import StatusField
from nautobot.extras.utils import extras_features
from nautobot.load_balancers import choices, constants


@extras_features("custom_links", "custom_validators", "export_templates", "graphql", "webhooks")
class VirtualServer(PrimaryModel):  # pylint: disable=too-many-ancestors
    """Virtual Server model for Load Balancer Models app."""

    vip = models.ForeignKey(
        to="ipam.IPAddress", on_delete=models.PROTECT, related_name="virtual_servers", verbose_name=_("VIP")
    )
    name = models.CharField(max_length=CHARFIELD_MAX_LENGTH, verbose_name=_("name"))
    port = models.PositiveIntegerField(
        blank=True, null=True, validators=[MaxValueValidator(constants.PORT_VALUE_MAX)], verbose_name=_("port")
    )
    protocol = models.CharField(
        max_length=CHARFIELD_MAX_LENGTH, blank=True, choices=choices.ProtocolChoices, verbose_name=_("protocol")
    )
    source_nat_pool = models.ForeignKey(
        to="ipam.Prefix",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="virtual_servers",
        verbose_name=_("Source NAT Pool"),
    )
    source_nat_type = models.CharField(
        max_length=CHARFIELD_MAX_LENGTH,
        choices=choices.SourceNATTypeChoices,
        blank=True,
        verbose_name=_("Source NAT Type"),
    )
    load_balancer_type = models.CharField(
        max_length=CHARFIELD_MAX_LENGTH,
        choices=choices.LoadBalancerTypeChoices,
        blank=True,
        verbose_name=_("load balancer type"),
    )
    enabled = models.BooleanField(default=True, verbose_name=_("enabled"))
    ssl_offload = models.BooleanField(default=False, verbose_name=_("SSL Offload"))
    # Assignment to a device, device redundancy group, cloud service or virtual chassis
    device = models.ForeignKey(
        to="dcim.Device",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="virtual_servers",
        verbose_name=_("device"),
    )
    device_redundancy_group = models.ForeignKey(
        to="dcim.DeviceRedundancyGroup",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="virtual_servers",
        verbose_name=_("device redundancy group"),
    )
    cloud_service = models.ForeignKey(
        to="cloud.CloudService",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="virtual_servers",
        verbose_name=_("cloud service"),
    )
    virtual_chassis = models.ForeignKey(
        to="dcim.VirtualChassis",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="virtual_servers",
        verbose_name=_("virtual chassis"),
    )
    tenant = models.ForeignKey(
        to="tenancy.Tenant",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="virtual_servers",
        verbose_name=_("tenant"),
    )
    load_balancer_pool = models.ForeignKey(
        to="load_balancers.LoadBalancerPool",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="virtual_servers",
        verbose_name=_("load balancer pool"),
    )
    health_check_monitor = models.ForeignKey(
        to="load_balancers.HealthCheckMonitor",
        related_name="virtual_servers",
        verbose_name=_("Health Check Monitor"),
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    certificate_profiles = models.ManyToManyField(
        to="load_balancers.CertificateProfile",
        related_name="virtual_servers",
        verbose_name=_("Certificate Profile"),
        blank=True,
        through="load_balancers.VirtualServerCertificateProfileAssignment",
    )

    clone_fields = [
        "port",
        "protocol",
        "source_nat_pool",
        "source_nat_type",
        "load_balancer_type",
        "enabled",
        "ssl_offload",
        "device",
        "device_redundancy_group",
        "cloud_service",
        "virtual_chassis",
        "tenant",
        "load_balancer_pool",
        "health_check_monitor",
    ]

    class Meta:
        """Meta class."""

        ordering = ["name"]
        unique_together = ["vip", "port", "protocol"]
        verbose_name = _("Virtual Server")

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
class LoadBalancerPool(PrimaryModel):  # pylint: disable=too-many-ancestors
    """LoadBalancerPool model for Load Balancer Models app."""

    name = models.CharField(max_length=CHARFIELD_MAX_LENGTH, verbose_name=_("name"))
    # We will attempt to use Constance for the load balancer algorithm options, or statically define in choices.
    load_balancing_algorithm = models.CharField(
        max_length=CHARFIELD_MAX_LENGTH,
        choices=choices.LoadBalancingAlgorithmChoices,
        verbose_name=_("load balancing algorithm"),
    )
    health_check_monitor = models.ForeignKey(
        to="load_balancers.HealthCheckMonitor",
        related_name="load_balancer_pools",
        verbose_name=_("Health Check Monitor"),
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    tenant = models.ForeignKey(
        to="tenancy.Tenant",
        related_name="load_balancer_pools",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name=_("tenant"),
    )

    natural_key_field_names = ["pk"]
    clone_fields = ["load_balancing_algorithm", "health_check_monitor", "tenant"]

    class Meta:
        """Meta class for LoadBalancerPool."""

        ordering = ["name"]
        verbose_name = _("Load Balancer Pool")

    def __str__(self):
        """Stringify instance."""
        return self.name


@extras_features(
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "statuses",
    "webhooks",
)
class LoadBalancerPoolMember(PrimaryModel):  # pylint: disable=too-many-ancestors
    """LoadBalancerPoolMember model for load_balancers."""

    label = models.CharField(
        max_length=CHARFIELD_MAX_LENGTH,
        blank=True,
        help_text=_("Optional label for the load balancer pool member."),
        verbose_name=_("label"),
    )
    ip_address = models.ForeignKey(
        to="ipam.IPAddress",
        related_name="load_balancer_pool_members",
        on_delete=models.CASCADE,
        verbose_name=_("IP Address"),
    )
    load_balancer_pool = models.ForeignKey(
        to="load_balancers.LoadBalancerPool",
        related_name="load_balancer_pool_members",
        on_delete=models.PROTECT,
        verbose_name=_("load balancer pool"),
    )
    port = models.PositiveIntegerField(validators=[MaxValueValidator(constants.PORT_VALUE_MAX)], verbose_name=_("port"))
    ssl_offload = models.BooleanField(
        default=False,
        verbose_name=_("SSL Offload"),
    )
    health_check_monitor = models.ForeignKey(
        to="load_balancers.HealthCheckMonitor",
        related_name="load_balancer_pool_members",
        verbose_name=_("Health Check Monitor"),
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    certificate_profiles = models.ManyToManyField(
        to="load_balancers.CertificateProfile",
        related_name="load_balancer_pool_members",
        verbose_name=_("Certificate Profile"),
        blank=True,
        through="load_balancers.LoadBalancerPoolMemberCertificateProfileAssignment",
    )
    tenant = models.ForeignKey(
        to="tenancy.Tenant",
        related_name="load_balancer_pool_members",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name=_("tenant"),
    )
    status = StatusField(blank=False, null=False, verbose_name=_("status"))

    clone_fields = [
        "load_balancer_pool",
        "port",
        "ssl_offload",
        "health_check_monitor",
        "tenant",
        "status",
    ]

    class Meta:
        """Meta class for LoadBalancerPoolMember."""

        unique_together = ["ip_address", "port", "load_balancer_pool"]
        verbose_name = _("Load Balancer Pool Member")

    def __str__(self):
        """Stringify instance."""
        return f"{self.ip_address.host}:{self.port}"

    @property
    def display(self):
        """Return a string display of the object."""
        return f"{self.ip_address.host}:{self.port}"


@extras_features("custom_links", "custom_validators", "export_templates", "graphql", "webhooks")
class HealthCheckMonitor(PrimaryModel):  # pylint: disable=too-many-ancestors
    """HealthCheckMonitor model for load_balancers."""

    name = models.CharField(max_length=CHARFIELD_MAX_LENGTH, unique=True, verbose_name=_("name"))
    interval = models.PositiveIntegerField(blank=True, null=True, verbose_name=_("interval"))
    retry = models.PositiveIntegerField(
        blank=True, null=True, help_text=_("Number of retries before marking as down"), verbose_name=_("retry")
    )
    timeout = models.PositiveIntegerField(blank=True, null=True, verbose_name=_("timeout"))
    port = models.PositiveIntegerField(
        blank=True, null=True, validators=[MaxValueValidator(constants.PORT_VALUE_MAX)], verbose_name=_("port")
    )
    health_check_type = models.CharField(
        max_length=CHARFIELD_MAX_LENGTH,
        choices=choices.HealthCheckTypeChoices,
        blank=True,
        verbose_name=_("health check type"),
    )
    tenant = models.ForeignKey(
        to="tenancy.Tenant",
        related_name="health_check_monitors",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name=_("tenant"),
    )
    clone_fields = ["interval", "retry", "timeout", "port", "health_check_type", "tenant"]

    class Meta:
        """Meta class for HealthCheckMonitor."""

        ordering = ["name"]
        verbose_name = _("Health Check Monitor")

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
class CertificateProfile(PrimaryModel):  # pylint: disable=too-many-ancestors
    """CertificateProfile model for load_balancers."""

    name = models.CharField(max_length=CHARFIELD_MAX_LENGTH, unique=True, verbose_name=_("name"))
    certificate_type = models.CharField(
        max_length=CHARFIELD_MAX_LENGTH,
        choices=choices.CertificateTypeChoices,
        blank=True,
        verbose_name=_("certificate type"),
    )
    certificate_file_path = models.CharField(
        max_length=CHARFIELD_MAX_LENGTH,
        blank=True,
        verbose_name=_("Certificate file path"),
    )
    chain_file_path = models.CharField(
        max_length=CHARFIELD_MAX_LENGTH,
        blank=True,
        verbose_name=_("Chain file path"),
    )
    key_file_path = models.CharField(
        max_length=CHARFIELD_MAX_LENGTH,
        blank=True,
        verbose_name=_("Key file path"),
    )
    expiration_date = models.DateTimeField(blank=True, null=True, verbose_name=_("expiration date"))
    cipher = models.CharField(max_length=CHARFIELD_MAX_LENGTH, blank=True, verbose_name=_("cipher"))
    tenant = models.ForeignKey(
        to="tenancy.Tenant",
        related_name="certificate_profiles",
        verbose_name=_("Tenant"),
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    clone_fields = [
        "certificate_type",
        "certificate_file_path",
        "chain_file_path",
        "key_file_path",
        "expiration_date",
        "cipher",
        "tenant",
    ]

    class Meta:
        """Meta class for CertificateProfile."""

        ordering = ["name"]
        verbose_name = _("Certificate Profile")

    def __str__(self):
        """Stringify instance."""
        return self.name


@extras_features(
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
)
class VirtualServerCertificateProfileAssignment(BaseModel):  # pylint: disable=too-many-ancestors
    """VirtualServerCertificateProfileAssignment model for load_balancers."""

    virtual_server = models.ForeignKey(
        to="load_balancers.VirtualServer",
        on_delete=models.CASCADE,
        related_name="certificate_profile_assignments",
        verbose_name=_("virtual server"),
    )
    certificate_profile = models.ForeignKey(
        to="load_balancers.CertificateProfile",
        on_delete=models.CASCADE,
        related_name="virtual_server_assignments",
        verbose_name=_("certificate profile"),
    )
    is_metadata_associable_model = False

    class Meta:
        """Meta class for VirtualServerCertificateProfileAssignment."""

        unique_together = ["virtual_server", "certificate_profile"]
        ordering = ["virtual_server", "certificate_profile"]

    def __str__(self):
        """Stringify instance."""
        return f"{self.virtual_server}: {self.certificate_profile}"


@extras_features(
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
)
class LoadBalancerPoolMemberCertificateProfileAssignment(BaseModel):  # pylint: disable=too-many-ancestors
    """LoadBalancerPoolMemberCertificateProfileAssignment model for load_balancers."""

    load_balancer_pool_member = models.ForeignKey(
        to="load_balancers.LoadBalancerPoolMember",
        on_delete=models.CASCADE,
        related_name="certificate_profile_assignments",
        verbose_name=_("load balancer pool member"),
    )
    certificate_profile = models.ForeignKey(
        to="load_balancers.CertificateProfile",
        on_delete=models.CASCADE,
        related_name="load_balancer_pool_member_assignments",
        verbose_name=_("certificate profile"),
    )
    is_metadata_associable_model = False

    class Meta:
        """Meta class for LoadBalancerPoolMemberCertificateProfileAssignment."""

        unique_together = ["load_balancer_pool_member", "certificate_profile"]
        ordering = ["load_balancer_pool_member", "certificate_profile"]

    def __str__(self):
        """Stringify instance."""
        return f"{self.load_balancer_pool_member}: {self.certificate_profile}"
