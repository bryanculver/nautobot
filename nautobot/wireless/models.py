from django.db import models
from django.utils.translation import gettext_lazy as _

from nautobot.core.constants import CHARFIELD_MAX_LENGTH
from nautobot.core.models import BaseModel
from nautobot.core.models.fields import JSONArrayField
from nautobot.core.models.generics import PrimaryModel
from nautobot.extras.utils import extras_features
from nautobot.wireless.choices import (
    RadioProfileChannelWidthChoices,
    RadioProfileFrequencyChoices,
    RadioProfileRegulatoryDomainChoices,
    SupportedDataRateStandardChoices,
    WirelessNetworkAuthenticationChoices,
    WirelessNetworkModeChoices,
)


@extras_features(
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "webhooks",
)
class SupportedDataRate(PrimaryModel):
    """
    A SupportedDataRate represents a data rate that can be used by an access point radio.
    """

    standard = models.CharField(
        max_length=CHARFIELD_MAX_LENGTH, choices=SupportedDataRateStandardChoices, verbose_name=_("standard")
    )
    rate = models.PositiveIntegerField(verbose_name=_("Rate (Kbps)"))
    mcs_index = models.IntegerField(
        blank=True,
        null=True,
        help_text=_(
            "The Modulation and Coding Scheme (MCS) index is a value used in wireless communications to define the modulation type, coding rate, and number of spatial streams used in a transmission."
        ),
        verbose_name=_("Modulation and Coding Scheme (MCS) Index"),
    )

    class Meta:
        ordering = ["standard", "rate"]
        unique_together = ["standard", "rate"]

    def __str__(self):
        return f"{self.standard}: {self.rate} Kbps"


@extras_features(
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "webhooks",
)
class RadioProfile(PrimaryModel):
    """
    A RadioProfile is a collection of settings that can be applied to an access point radio.
    """

    name = models.CharField(max_length=CHARFIELD_MAX_LENGTH, unique=True, verbose_name=_("name"))
    frequency = models.CharField(
        max_length=CHARFIELD_MAX_LENGTH, choices=RadioProfileFrequencyChoices, blank=True, verbose_name=_("frequency")
    )
    tx_power_min = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_("Transmit Power Minimum"),
    )
    tx_power_max = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_("Transmit Power Maximum"),
    )
    channel_width = JSONArrayField(
        base_field=models.IntegerField(choices=RadioProfileChannelWidthChoices),
        blank=True,
        null=True,
        verbose_name=_("channel width"),
    )
    allowed_channel_list = JSONArrayField(
        base_field=models.IntegerField(),
        blank=True,
        null=True,
        help_text=_("Comma-separated list of allowed channel numbers for this radio profile."),
        verbose_name=_("allowed channel list"),
    )
    supported_data_rates = models.ManyToManyField(
        to="wireless.SupportedDataRate",
        related_name="radio_profiles",
        blank=True,
        verbose_name=_("supported data rates"),
    )
    regulatory_domain = models.CharField(
        max_length=CHARFIELD_MAX_LENGTH,
        choices=RadioProfileRegulatoryDomainChoices,
        verbose_name=_("regulatory domain"),
    )
    rx_power_min = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_("Receive Power Minimum"),
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


@extras_features(
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "webhooks",
)
class WirelessNetwork(PrimaryModel):
    """
    A WirelessNetwork represents a wireless network that can be broadcast by an access point.
    """

    name = models.CharField(max_length=CHARFIELD_MAX_LENGTH, unique=True, verbose_name=_("name"))
    description = models.CharField(max_length=CHARFIELD_MAX_LENGTH, blank=True, verbose_name=_("description"))
    ssid = models.CharField(max_length=CHARFIELD_MAX_LENGTH, verbose_name=_("SSID"))
    mode = models.CharField(max_length=CHARFIELD_MAX_LENGTH, choices=WirelessNetworkModeChoices, verbose_name=_("mode"))
    enabled = models.BooleanField(default=True, verbose_name=_("enabled"))
    authentication = models.CharField(
        max_length=CHARFIELD_MAX_LENGTH, choices=WirelessNetworkAuthenticationChoices, verbose_name=_("authentication")
    )
    secrets_group = models.ForeignKey(
        to="extras.SecretsGroup",
        on_delete=models.PROTECT,
        related_name="wireless_networks",
        blank=True,
        null=True,
        verbose_name=_("secrets group"),
    )
    hidden = models.BooleanField(default=False, verbose_name=_("hidden"))
    tenant = models.ForeignKey(
        to="tenancy.Tenant",
        on_delete=models.PROTECT,
        related_name="wireless_networks",
        blank=True,
        null=True,
        verbose_name=_("tenant"),
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


@extras_features(
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
)
class ControllerManagedDeviceGroupWirelessNetworkAssignment(BaseModel):
    """
    A ControllerManagedDeviceGroupWirelessNetworkAssignment represents the assignment of a WirelessNetwork to an ControllerManagedDeviceGroup.
    """

    controller_managed_device_group = models.ForeignKey(
        to="dcim.ControllerManagedDeviceGroup",
        on_delete=models.CASCADE,
        related_name="wireless_network_assignments",
        verbose_name=_("controller managed device group"),
    )
    wireless_network = models.ForeignKey(
        to="wireless.WirelessNetwork",
        on_delete=models.CASCADE,
        related_name="controller_managed_device_group_assignments",
        verbose_name=_("wireless network"),
    )
    vlan = models.ForeignKey(
        to="ipam.VLAN",
        on_delete=models.PROTECT,
        related_name="controller_managed_device_group_wireless_network_assignments",
        blank=True,
        null=True,
        verbose_name=_("vlan"),
    )
    is_metadata_associable_model = False
    documentation_static_path = "docs/user-guide/core-data-model/dcim/controllermanageddevicegroup.html"

    class Meta:
        unique_together = ["controller_managed_device_group", "wireless_network"]
        ordering = ["controller_managed_device_group", "wireless_network"]

    def __str__(self):
        return f"{self.controller_managed_device_group}: {self.wireless_network}"


@extras_features(
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
)
class ControllerManagedDeviceGroupRadioProfileAssignment(BaseModel):
    """
    A ControllerManagedDeviceGroupRadioProfile represents the assignment of a RadioProfile to an ControllerManagedDeviceGroup.
    """

    controller_managed_device_group = models.ForeignKey(
        to="dcim.ControllerManagedDeviceGroup",
        on_delete=models.CASCADE,
        related_name="radio_profile_assignments",
        verbose_name=_("controller managed device group"),
    )
    radio_profile = models.ForeignKey(
        to="wireless.RadioProfile",
        on_delete=models.CASCADE,
        related_name="controller_managed_device_group_assignments",
        verbose_name=_("radio profile"),
    )
    is_metadata_associable_model = False
    documentation_static_path = "docs/user-guide/core-data-model/dcim/controllermanageddevicegroup.html"

    class Meta:
        unique_together = ["controller_managed_device_group", "radio_profile"]
        ordering = ["controller_managed_device_group", "radio_profile"]

    def __str__(self):
        return f"{self.controller_managed_device_group}: {self.radio_profile}"
