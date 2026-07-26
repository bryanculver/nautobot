from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext, gettext_lazy as _

from nautobot.core.constants import CHARFIELD_MAX_LENGTH
from nautobot.core.models.generics import PrimaryModel
from nautobot.core.models.validators import ExclusionValidator
from nautobot.core.utils.data import UtilizationData
from nautobot.dcim.choices import (
    PowerFeedBreakerPoleChoices,
    PowerFeedPhaseChoices,
    PowerFeedSupplyChoices,
    PowerFeedTypeChoices,
    PowerPanelTypeChoices,
    PowerPathChoices,
)
from nautobot.dcim.constants import (
    POWERFEED_AMPERAGE_DEFAULT,
    POWERFEED_MAX_UTILIZATION_DEFAULT,
    POWERFEED_VOLTAGE_DEFAULT,
)
from nautobot.dcim.models.device_components import CableTerminationManager, PowerPort
from nautobot.extras.models import StatusField
from nautobot.extras.utils import extras_features

from .device_components import CableTermination, PathEndpoint

__all__ = (
    "PowerFeed",
    "PowerPanel",
)


#
# Power
#


@extras_features(
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "locations",
    "webhooks",
)
class PowerPanel(PrimaryModel):
    """
    A distribution point for electrical power; e.g. a data center RPP.
    """

    location = models.ForeignKey(
        to="dcim.Location", on_delete=models.PROTECT, related_name="power_panels", verbose_name=_("location")
    )
    rack_group = models.ForeignKey(
        to="RackGroup",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="power_panels",
        verbose_name=_("rack group"),
    )
    name = models.CharField(max_length=CHARFIELD_MAX_LENGTH, db_index=True, verbose_name=_("name"))
    panel_type = models.CharField(
        max_length=30, choices=PowerPanelTypeChoices, blank=True, verbose_name=_("panel type")
    )
    breaker_position_count = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_("Total number of breaker positions in the panel (e.g., 42)"),
        verbose_name=_("breaker position count"),
    )
    power_path = models.CharField(
        max_length=20,
        choices=PowerPathChoices,
        help_text=_("Physical power distribution redundancy path."),
        blank=True,
        verbose_name=_("power path"),
    )

    natural_key_field_names = ["name", "location"]

    class Meta:
        ordering = ["location", "name"]
        unique_together = ["location", "name"]

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()

        # Validate location
        if self.location is not None:
            if ContentType.objects.get_for_model(self) not in self.location.location_type.content_types.all():
                raise ValidationError(
                    {
                        "location": gettext('Power panels may not associate to locations of type "%(location_type)s".')
                        % {"location_type": self.location.location_type}
                    }
                )

        # RackGroup must belong to assigned Location
        if self.rack_group:
            if (
                self.location is not None
                and self.rack_group.location is not None  # pylint: disable=no-member
                and self.rack_group.location not in self.location.ancestors(include_self=True)  # pylint: disable=no-member
            ):
                raise ValidationError(
                    {  # pylint: disable=no-member  # false positive on rack_group.location
                        "rack_group": gettext(
                            'Rack group "%(rack_group)s" belongs to a location ("%(location)s") that does not contain "%(location_2)s".'
                        )
                        % {
                            "rack_group": self.rack_group,
                            "location": self.rack_group.location,
                            "location_2": self.location,
                        }
                    }
                )


@extras_features(
    "cable_terminations",
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "statuses",
    "webhooks",
)
class PowerFeed(PrimaryModel, PathEndpoint, CableTermination):
    """
    An electrical circuit delivered from a PowerPanel.
    """

    objects = CableTerminationManager()

    power_panel = models.ForeignKey(
        to="PowerPanel",
        on_delete=models.PROTECT,
        related_name="power_feeds",
        help_text=_("Source panel that originates this power feed"),
        verbose_name=_("power panel"),
    )
    destination_panel = models.ForeignKey(
        to="PowerPanel",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="feeders",
        help_text=_("Destination panel that receives power from this feed"),
        verbose_name=_("destination panel"),
    )
    rack = models.ForeignKey(
        to="Rack", on_delete=models.PROTECT, blank=True, null=True, related_name="power_feeds", verbose_name=_("rack")
    )
    name = models.CharField(max_length=CHARFIELD_MAX_LENGTH, verbose_name=_("name"))
    status = StatusField(blank=False, null=False, verbose_name=_("status"))
    type = models.CharField(
        max_length=50, choices=PowerFeedTypeChoices, default=PowerFeedTypeChoices.TYPE_PRIMARY, verbose_name=_("type")
    )
    power_path = models.CharField(
        max_length=20,
        choices=PowerPathChoices,
        help_text=_("Physical power distribution redundancy path."),
        blank=True,
        verbose_name=_("power path"),
    )
    supply = models.CharField(
        max_length=50,
        choices=PowerFeedSupplyChoices,
        default=PowerFeedSupplyChoices.SUPPLY_AC,
        verbose_name=_("supply"),
    )
    phase = models.CharField(
        max_length=50,
        choices=PowerFeedPhaseChoices,
        default=PowerFeedPhaseChoices.PHASE_SINGLE,
        verbose_name=_("phase"),
    )
    voltage = models.SmallIntegerField(
        default=POWERFEED_VOLTAGE_DEFAULT, validators=[ExclusionValidator([0])], verbose_name=_("voltage")
    )
    amperage = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)], default=POWERFEED_AMPERAGE_DEFAULT, verbose_name=_("amperage")
    )
    max_utilization = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        default=POWERFEED_MAX_UTILIZATION_DEFAULT,
        help_text=_("Maximum permissible draw (percentage)"),
        verbose_name=_("max utilization"),
    )
    breaker_position = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_("Starting circuit breaker position in panel"),
        verbose_name=_("breaker position"),
    )
    breaker_pole_count = models.PositiveSmallIntegerField(
        choices=PowerFeedBreakerPoleChoices,
        blank=True,
        null=True,
        help_text=_("Number of breaker poles"),
        verbose_name=_("breaker pole count"),
    )
    available_power = models.PositiveIntegerField(default=0, editable=False)
    comments = models.TextField(blank=True, verbose_name=_("comments"))

    clone_fields = [
        "power_panel",
        "destination_panel",
        "rack",
        "status",
        "type",
        "supply",
        "phase",
        "voltage",
        "amperage",
        "max_utilization",
        "breaker_pole_count",
        "available_power",
    ]

    class Meta:
        ordering = ["power_panel", "breaker_position", "name"]
        unique_together = [
            ["power_panel", "name"],
            ["power_panel", "breaker_position"],
        ]
        indexes = [
            models.Index(fields=["power_panel", "breaker_position"]),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()

        # Rack must belong to same location hierarchy as PowerPanel
        if self.rack and self.power_panel.location:  # pylint: disable=no-member
            if self.rack.location not in self.power_panel.location.ancestors(  # pylint: disable=no-member
                include_self=True
            ) and self.power_panel.location not in self.rack.location.ancestors(include_self=True):  # pylint: disable=no-member
                raise ValidationError(
                    {
                        "rack": gettext(
                            'Rack "%(rack)s" (%(location)s) and power panel "%(power_panel)s" (%(location_2)s) are not in the same location hierarchy.'
                        )
                        % {
                            "rack": self.rack,
                            "location": self.rack.location,
                            "power_panel": self.power_panel,
                            "location_2": self.power_panel.location,
                        }
                    }
                )

        # AC voltage cannot be negative
        if self.voltage < 0 and self.supply == PowerFeedSupplyChoices.SUPPLY_AC:
            raise ValidationError({"voltage": _("Voltage cannot be negative for AC supply")})

        # Destination panel validation
        if self.destination_panel:
            # Cannot feed into the same panel
            if self.destination_panel == self.power_panel:
                raise ValidationError({"destination_panel": _("A power feed cannot connect a panel to itself")})
            # TODO: add loop detection when graph structure is implemented for path tracing

        # Enforce mutual exclusivity between cable connections and destination_panel
        if self.destination_panel and self.cable:
            raise ValidationError(
                {
                    "destination_panel": _(
                        "Cannot specify a destination panel when the power feed is connected via cable. "
                        "Power feeds can either connect to a panel OR be cabled to an endpoint, but not both."
                    )
                }
            )

        # Breaker position and pole validation
        if self.breaker_position is not None:
            # Default to single pole breaker when breaker_position is specified but breaker_pole_count is not
            if self.breaker_pole_count is None:
                self.breaker_pole_count = PowerFeedBreakerPoleChoices.POLE_1

            # Get occupied positions once for both validations
            occupied_positions = self.get_occupied_positions()

            # Ensure breaker positions fit within panel capacity
            if self.power_panel.breaker_position_count is not None:
                if occupied_positions:
                    max_occupied_position = max(occupied_positions)
                    if max_occupied_position > self.power_panel.breaker_position_count:
                        raise ValidationError(
                            {
                                "breaker_position": gettext(
                                    "Breaker configuration starting at position %(breaker_position)s with %(breaker_pole_count)s poles would occupy positions %(occupied_positions)s, but panel only has %(breaker_position_count)s breaker positions"
                                )
                                % {
                                    "breaker_position": self.breaker_position,
                                    "breaker_pole_count": self.breaker_pole_count,
                                    "occupied_positions": sorted(occupied_positions),
                                    "breaker_position_count": self.power_panel.breaker_position_count,
                                }
                            }
                        )

            # Check for breaker position conflicts with other feeds
            conflicts = PowerFeed.objects.filter(
                power_panel=self.power_panel, breaker_position__isnull=False, breaker_pole_count__isnull=False
            ).exclude(pk=self.pk)

            for feed in conflicts:
                if occupied_positions.intersection(feed.get_occupied_positions()):
                    raise ValidationError(
                        {
                            "breaker_position": gettext(
                                'Breaker position %(breaker_position)s conflicts with feed "%(name)s" (occupies %(occupied_positions)s)'
                            )
                            % {
                                "breaker_position": self.breaker_position,
                                "name": feed.name,
                                "occupied_positions": feed.occupied_positions,
                            }
                        }
                    )

    def save(self, *args, **kwargs):
        # Enforce breaker pole count default
        if self.breaker_position is not None and self.breaker_pole_count is None:
            self.breaker_pole_count = PowerFeedBreakerPoleChoices.POLE_1

        # Enforce mutual exclusivity between cable connections and destination_panel
        if self.destination_panel and self.cable:
            raise ValidationError(
                _(
                    "Cannot specify a destination panel when the power feed is connected via cable. "
                    "Power feeds can either connect to a panel OR be cabled to an endpoint, but not both."
                )
            )

        # Cache the available_power property on the instance
        kva = abs(self.voltage) * self.amperage * (self.max_utilization / 100)
        if self.phase == PowerFeedPhaseChoices.PHASE_3PHASE:
            self.available_power = round(kva * 1.732)
        else:
            self.available_power = round(kva)

        super().save(*args, **kwargs)

    @property
    def parent(self):
        return self.power_panel

    @property
    def occupied_positions(self) -> str:
        """All circuit positions occupied by this feed as comma-separated string."""
        positions = self.get_occupied_positions()
        return ", ".join(map(str, sorted(positions))) if positions else ""

    @property
    def phase_designation(self):
        """Calculate phase designation based on occupied circuit positions."""
        if not (self.breaker_position and self.breaker_pole_count):
            return None

        positions = self.get_occupied_positions()
        if not positions:
            return None

        # Positions 1,2=A, 3,4=B, 5,6=C, 7,8=A, 9,10=B, 11,12=C, etc.
        def position_to_phase(pos):
            # Calculate which phase this position is on
            cycle_position = ((pos - 1) // 2) % 3
            return ["A", "B", "C"][cycle_position]

        phases = {position_to_phase(pos) for pos in positions}

        # Return phase designation based on which phases are used
        if len(phases) == 1:
            return next(iter(phases))  # Single phase: "A", "B", or "C"
        elif len(phases) == 2:
            sorted_phases = sorted(phases)
            return f"{sorted_phases[0]}-{sorted_phases[1]}"  # "A-B", "B-C", etc.
        elif len(phases) == 3:
            return "A-B-C"  # Three-phase
        else:
            return None

    def get_occupied_positions(self) -> set[int]:
        """Get set of circuit breaker positions occupied by this feed."""
        if not (self.breaker_position and self.breaker_pole_count):
            return set()

        return set(self.breaker_position + (i * 2) for i in range(self.breaker_pole_count))

    def get_type_class(self):
        return PowerFeedTypeChoices.CSS_CLASSES.get(self.type)

    @property
    def utilization(self):
        power_port = self.connected_endpoint
        if not isinstance(power_port, PowerPort):
            return None
        utilization = power_port.get_power_draw()
        allocated = utilization["allocated"]
        available = self.available_power or 0
        return UtilizationData(numerator=allocated, denominator=available)
