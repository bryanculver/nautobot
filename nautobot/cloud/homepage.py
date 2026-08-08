from django.utils.translation import gettext_lazy as _

from nautobot.cloud.models import CloudAccount, CloudNetwork, CloudResourceType, CloudService
from nautobot.core.apps import HomePageItem, HomePagePanel

layout = (
    HomePagePanel(
        name="Cloud",
        label=_("Cloud"),
        weight=500,
        items=(
            HomePageItem(
                name="Cloud Accounts",
                label=_("Cloud Accounts"),
                link="cloud:cloudaccount_list",
                model=CloudAccount,
                description=_("Account tracking for public and private cloud providers"),
                permissions=["cloud.view_cloudaccount"],
                weight=100,
            ),
            HomePageItem(
                name="Cloud Resource Types",
                label=_("Cloud Resource Types"),
                link="cloud:cloudresourcetype_list",
                model=CloudResourceType,
                description=_("Resource types for public and private cloud providers"),
                permissions=["cloud.view_cloudresourcetype"],
                weight=200,
            ),
            HomePageItem(
                name="Cloud Networks",
                label=_("Cloud Networks"),
                link="cloud:cloudnetwork_list",
                model=CloudNetwork,
                description=_("Networks for public and private cloud providers"),
                permissions=["cloud.view_cloudnetwork"],
                weight=300,
            ),
            HomePageItem(
                name="Cloud Services",
                label=_("Cloud Services"),
                link="cloud:cloudservice_list",
                model=CloudService,
                description=_("Services for public and private cloud providers"),
                permissions=["cloud.view_cloudservice"],
                weight=400,
            ),
        ),
    ),
)
