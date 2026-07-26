from django.utils.translation import gettext_lazy as _

from nautobot.core.choices import ChoiceSet

#
# Circuits
#


class CircuitStatusChoices(ChoiceSet):
    STATUS_DEPROVISIONING = "deprovisioning"
    STATUS_ACTIVE = "active"
    STATUS_PLANNED = "planned"
    STATUS_PROVISIONING = "provisioning"
    STATUS_OFFLINE = "offline"
    STATUS_DECOMMISSIONED = "decommissioned"

    CHOICES = (
        (STATUS_PLANNED, _("Planned")),
        (STATUS_PROVISIONING, _("Provisioning")),
        (STATUS_ACTIVE, _("Active")),
        (STATUS_OFFLINE, _("Offline")),
        (STATUS_DEPROVISIONING, _("Deprovisioning")),
        (STATUS_DECOMMISSIONED, _("Decommissioned")),
    )


#
# CircuitTerminations
#


class CircuitTerminationSideChoices(ChoiceSet):
    SIDE_A = "A"
    SIDE_Z = "Z"

    CHOICES = ((SIDE_A, _("A")), (SIDE_Z, _("Z")))
