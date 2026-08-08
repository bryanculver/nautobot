from django.utils.translation import gettext_lazy as _

from nautobot.core.apps import HomePageItem, HomePagePanel
from nautobot.tenancy.models import Tenant

layout = (
    HomePagePanel(
        name="Organization",
        label=_("Organization"),
        weight=100,
        items=(
            HomePageItem(
                name="Tenants",
                label=_("Tenants"),
                link="tenancy:tenant_list",
                model=Tenant,
                description=_("Customers or departments"),
                permissions=["tenancy.view_tenant"],
                weight=200,
            ),
        ),
    ),
)
