from django.utils.translation import gettext_lazy as _

from nautobot.core.choices import ChoiceSet

#
# VirtualMachines
#


class VirtualMachineStatusChoices(ChoiceSet):
    STATUS_OFFLINE = "offline"
    STATUS_ACTIVE = "active"
    STATUS_PLANNED = "planned"
    STATUS_STAGED = "staged"
    STATUS_FAILED = "failed"
    STATUS_DECOMMISSIONING = "decommissioning"

    CHOICES = (
        (STATUS_OFFLINE, _("Offline")),
        (STATUS_ACTIVE, _("Active")),
        (STATUS_PLANNED, _("Planned")),
        (STATUS_STAGED, _("Staged")),
        (STATUS_FAILED, _("Failed")),
        (STATUS_DECOMMISSIONING, _("Decommissioning")),
    )


class VMInterfaceStatusChoices(ChoiceSet):
    STATUS_ACTIVE = "active"
    STATUS_DECOMMISSIONING = "decommissioning"
    STATUS_FAILED = "failed"
    STATUS_MAINTENANCE = "maintenance"
    STATUS_PLANNED = "planned"

    CHOICES = (
        (STATUS_FAILED, _("Failed")),
        (STATUS_ACTIVE, _("Active")),
        (STATUS_DECOMMISSIONING, _("Decommissioning")),
        (STATUS_MAINTENANCE, _("Maintenance")),
        (STATUS_PLANNED, _("Planned")),
    )
