from django.utils.translation import gettext_lazy as _

from nautobot.circuits.models import Circuit, Provider
from nautobot.core.apps import HomePageItem, HomePagePanel

layout = (
    HomePagePanel(
        name="Circuits",
        label=_("Circuits"),
        weight=500,
        items=(
            HomePageItem(
                name="Providers",
                label=_("Providers"),
                link="circuits:provider_list",
                model=Provider,
                description=_("Organizations which provide circuit connectivity"),
                permissions=["circuits.view_provider"],
                weight=100,
            ),
            HomePageItem(
                name="Circuits",
                label=_("Circuits"),
                link="circuits:circuit_list",
                model=Circuit,
                description=_("Communication links for Internet transit, peering, and other services"),
                permissions=["circuits.view_circuit"],
                weight=200,
            ),
        ),
    ),
)
