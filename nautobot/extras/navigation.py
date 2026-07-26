from django.utils.translation import gettext_lazy as _

from nautobot.core.apps import (
    NavMenuAddButton,
    NavMenuGroup,
    NavMenuItem,
    NavMenuTab,
)
from nautobot.core.ui.choices import NavigationIconChoices, NavigationWeightChoices

menu_items = (
    NavMenuTab(
        name="Approvals",
        label=_("Approvals"),
        icon=NavigationIconChoices.APPROVAL_WORKFLOWS,
        weight=NavigationWeightChoices.APPROVAL_WORKFLOWS,
        groups=(
            NavMenuGroup(
                name="Approval Workflows",
                label=_("Approval Workflows"),
                weight=50,
                items=(
                    NavMenuItem(
                        link="extras:approvalworkflowdefinition_list",
                        name="Workflow Definitions",
                        label=_("Workflow Definitions"),
                        weight=100,
                        permissions=["extras.view_approvalworkflowdefinition"],
                        buttons=(
                            NavMenuAddButton(
                                link="extras:approvalworkflowdefinition_add",
                                permissions=["extras.add_approvalworkflowdefinition"],
                            ),
                        ),
                    ),
                    NavMenuItem(
                        link="extras:approver_dashboard",
                        name="Approval Dashboard",
                        label=_("Approval Dashboard"),
                        weight=200,
                        permissions=["extras.view_approvalworkflow"],
                    ),
                ),
            ),
        ),
    ),
    NavMenuTab(
        name="Organization",
        label=_("Organization"),
        icon=NavigationIconChoices.ORGANIZATION,
        weight=NavigationWeightChoices.ORGANIZATION,
        groups=(
            NavMenuGroup(
                name="Contacts",
                label=_("Contacts"),
                weight=400,
                items=(
                    NavMenuItem(
                        link="extras:contact_list",
                        name="Contacts",
                        label=_("Contacts"),
                        weight=100,
                        permissions=["extras.view_contact"],
                        buttons=[NavMenuAddButton(link="extras:contact_add", permissions=["extras.add_contact"])],
                    ),
                    NavMenuItem(
                        link="extras:team_list",
                        name="Teams",
                        label=_("Teams"),
                        weight=200,
                        permissions=["extras.view_team"],
                        buttons=[NavMenuAddButton(link="extras:team_add", permissions=["extras.add_team"])],
                    ),
                ),
            ),
            NavMenuGroup(
                name="Groups",
                label=_("Groups"),
                weight=500,
                items=(
                    NavMenuItem(
                        link="extras:dynamicgroup_list",
                        name="Dynamic Groups",
                        label=_("Dynamic Groups"),
                        weight=100,
                        permissions=[
                            "extras.view_dynamicgroup",
                        ],
                        buttons=(
                            NavMenuAddButton(
                                link="extras:dynamicgroup_add",
                                permissions=[
                                    "extras.add_dynamicgroup",
                                ],
                            ),
                        ),
                    ),
                ),
            ),
            NavMenuGroup(
                name="Metadata",  # TODO: is there a better name for this grouping?
                label=_("Metadata"),
                weight=600,
                items=(
                    NavMenuItem(
                        link="extras:tag_list",
                        name="Tags",
                        label=_("Tags"),
                        weight=100,
                        permissions=[
                            "extras.view_tag",
                        ],
                        buttons=(
                            NavMenuAddButton(
                                link="extras:tag_add",
                                permissions=[
                                    "extras.add_tag",
                                ],
                            ),
                        ),
                    ),
                    NavMenuItem(
                        link="extras:status_list",
                        name="Statuses",
                        label=_("Statuses"),
                        weight=200,
                        permissions=[
                            "extras.view_status",
                        ],
                        buttons=(
                            NavMenuAddButton(
                                link="extras:status_add",
                                permissions=[
                                    "extras.add_status",
                                ],
                            ),
                        ),
                    ),
                    NavMenuItem(
                        link="extras:role_list",
                        name="Roles",
                        label=_("Roles"),
                        weight=300,
                        permissions=[
                            "extras.view_role",
                        ],
                        buttons=(
                            NavMenuAddButton(
                                link="extras:role_add",
                                permissions=[
                                    "extras.add_role",
                                ],
                            ),
                        ),
                    ),
                ),
            ),
        ),
    ),
    NavMenuTab(
        name="Secrets",
        label=_("Secrets"),
        icon=NavigationIconChoices.SECRETS,
        weight=NavigationWeightChoices.SECRETS,
        groups=(
            NavMenuGroup(
                name="Secrets",
                label=_("Secrets"),
                weight=100,
                items=(
                    NavMenuItem(
                        link="extras:secret_list",
                        name="Secrets",
                        label=_("Secrets"),
                        weight=100,
                        permissions=["extras.view_secret"],
                        buttons=(NavMenuAddButton(link="extras:secret_add", permissions=["extras.add_secret"]),),
                    ),
                    NavMenuItem(
                        link="extras:secretsgroup_list",
                        name="Secrets Groups",
                        label=_("Secrets Groups"),
                        weight=200,
                        permissions=["extras.view_secretsgroup"],
                        buttons=(
                            NavMenuAddButton(link="extras:secretsgroup_add", permissions=["extras.add_secretsgroup"]),
                        ),
                    ),
                ),
            ),
        ),
    ),
    NavMenuTab(
        name="Jobs",
        label=_("Jobs"),
        icon=NavigationIconChoices.JOBS,
        weight=NavigationWeightChoices.JOBS,
        groups=(
            NavMenuGroup(
                name="Jobs",
                label=_("Jobs"),
                weight=100,
                items=(
                    NavMenuItem(
                        link="extras:job_list",
                        name="Jobs",
                        label=_("Jobs"),
                        weight=100,
                        permissions=[
                            "extras.view_job",
                        ],
                        buttons=(),
                    ),
                    NavMenuItem(
                        link="extras:scheduledjob_list",
                        name="Scheduled Jobs",
                        label=_("Scheduled Jobs"),
                        weight=300,
                        permissions=[
                            "extras.view_job",
                            "extras.view_scheduledjob",
                        ],
                        buttons=(),
                    ),
                    NavMenuItem(
                        link="extras:jobresult_list",
                        name="Job Results",
                        label=_("Job Results"),
                        weight=400,
                        permissions=[
                            "extras.view_jobresult",
                        ],
                        buttons=(),
                    ),
                    NavMenuItem(
                        link="extras:jobhook_list",
                        name="Job Hooks",
                        label=_("Job Hooks"),
                        weight=500,
                        permissions=[
                            "extras.view_jobhook",
                        ],
                        buttons=(
                            NavMenuAddButton(
                                link="extras:jobhook_add",
                                permissions=[
                                    "extras.add_jobhook",
                                ],
                            ),
                        ),
                    ),
                    NavMenuItem(
                        link="extras:jobbutton_list",
                        name="Job Buttons",
                        label=_("Job Buttons"),
                        weight=600,
                        permissions=[
                            "extras.view_jobbutton",
                        ],
                        buttons=(
                            NavMenuAddButton(
                                link="extras:jobbutton_add",
                                permissions=[
                                    "extras.add_jobbutton",
                                ],
                            ),
                        ),
                    ),
                    NavMenuItem(
                        link="extras:jobqueue_list",
                        name="Job Queues",
                        label=_("Job Queues"),
                        weight=700,
                        permissions=[
                            "extras.view_jobqueue",
                        ],
                        buttons=(
                            NavMenuAddButton(
                                link="extras:jobqueue_add",
                                permissions=[
                                    "extras.add_jobqueue",
                                ],
                            ),
                        ),
                    ),
                ),
            ),
        ),
    ),
    NavMenuTab(
        name="Extensibility",
        label=_("Extensibility"),
        icon=NavigationIconChoices.EXTENSIBILITY,
        weight=NavigationWeightChoices.EXTENSIBILITY,
        groups=(
            NavMenuGroup(
                name="Logging",
                label=_("Logging"),
                weight=100,
                items=(
                    NavMenuItem(
                        link="extras:objectchange_list",
                        name="Change Log",
                        label=_("Change Log"),
                        weight=100,
                        permissions=[
                            "extras.view_objectchange",
                        ],
                        buttons=(),
                    ),
                ),
            ),
            NavMenuGroup(
                name="Users",
                label=_("Users"),
                weight=150,
                items=(
                    NavMenuItem(
                        link="extras:savedview_list",
                        name="Saved Views",
                        label=_("Saved Views"),
                        weight=100,
                        permissions=[
                            "extras.view_savedview",
                        ],
                    ),
                ),
            ),
            NavMenuGroup(
                name="Data Sources",
                label=_("Data Sources"),
                weight=200,
                items=(
                    NavMenuItem(
                        link="extras:gitrepository_list",
                        name="Git Repositories",
                        label=_("Git Repositories"),
                        weight=100,
                        permissions=[
                            "extras.view_gitrepository",
                        ],
                        buttons=(
                            NavMenuAddButton(
                                link="extras:gitrepository_add",
                                permissions=[
                                    "extras.add_gitrepository",
                                ],
                            ),
                        ),
                    ),
                ),
            ),
            NavMenuGroup(
                name="Data Management",
                label=_("Data Management"),
                weight=300,
                items=(
                    NavMenuItem(
                        link="extras:graphqlquery_list",
                        name="GraphQL Queries",
                        label=_("GraphQL Queries"),
                        weight=100,
                        permissions=[
                            "extras.view_graphqlquery",
                        ],
                        buttons=(
                            NavMenuAddButton(
                                link="extras:graphqlquery_add",
                                permissions=[
                                    "extras.add_graphqlquery",
                                ],
                            ),
                        ),
                    ),
                    NavMenuItem(
                        link="extras:note_list",
                        name="Notes",
                        label=_("Notes"),
                        weight=300,
                        permissions=[
                            "extras.view_note",
                        ],
                    ),
                ),
            ),
            NavMenuGroup(
                name="Automation",
                label=_("Automation"),
                weight=500,
                items=(
                    NavMenuItem(
                        link="extras:configcontext_list",
                        name="Config Contexts",
                        label=_("Config Contexts"),
                        weight=100,
                        permissions=[
                            "extras.view_configcontext",
                        ],
                        buttons=(
                            NavMenuAddButton(
                                link="extras:configcontext_add",
                                permissions=[
                                    "extras.add_configcontext",
                                ],
                            ),
                        ),
                    ),
                    NavMenuItem(
                        link="extras:configcontextschema_list",
                        name="Config Context Schemas",
                        label=_("Config Context Schemas"),
                        weight=100,
                        permissions=[
                            "extras.view_configcontextschema",
                        ],
                        buttons=(
                            NavMenuAddButton(
                                link="extras:configcontextschema_add",
                                permissions=[
                                    "extras.add_configcontextschema",
                                ],
                            ),
                        ),
                    ),
                    NavMenuItem(
                        link="extras:exporttemplate_list",
                        name="Export Templates",
                        label=_("Export Templates"),
                        weight=200,
                        permissions=[
                            "extras.view_exporttemplate",
                        ],
                        buttons=(
                            NavMenuAddButton(
                                link="extras:exporttemplate_add",
                                permissions=[
                                    "extras.add_exporttemplate",
                                ],
                            ),
                        ),
                    ),
                    NavMenuItem(
                        link="extras:externalintegration_list",
                        name="External Integrations",
                        label=_("External Integrations"),
                        weight=300,
                        permissions=[
                            "extras.view_externalintegration",
                        ],
                        buttons=(
                            NavMenuAddButton(
                                link="extras:externalintegration_add",
                                permissions=[
                                    "extras.add_externalintegration",
                                ],
                            ),
                        ),
                    ),
                    NavMenuItem(
                        link="extras:webhook_list",
                        name="Webhooks",
                        label=_("Webhooks"),
                        weight=400,
                        permissions=[
                            "extras.view_webhook",
                        ],
                        buttons=(
                            NavMenuAddButton(
                                link="extras:webhook_add",
                                permissions=[
                                    "extras.add_webhook",
                                ],
                            ),
                        ),
                    ),
                ),
            ),
            NavMenuGroup(
                name="Data Model",
                label=_("Data Model"),
                weight=600,
                items=(
                    NavMenuItem(
                        link="extras:customfield_list",
                        name="Custom Fields",
                        label=_("Custom Fields"),
                        weight=100,
                        permissions=[
                            "extras.view_customfield",
                        ],
                        buttons=(
                            NavMenuAddButton(
                                link="extras:customfield_add",
                                permissions=[
                                    "extras.add_customfield",
                                ],
                            ),
                        ),
                    ),
                    NavMenuItem(
                        link="extras:relationship_list",
                        name="Relationships",
                        label=_("Relationships"),
                        weight=200,
                        permissions=[
                            "extras.view_relationship",
                        ],
                        buttons=(
                            NavMenuAddButton(
                                link="extras:relationship_add",
                                permissions=[
                                    "extras.add_relationship",
                                ],
                            ),
                        ),
                    ),
                    NavMenuItem(
                        link="extras:computedfield_list",
                        name="Computed Fields",
                        label=_("Computed Fields"),
                        weight=300,
                        permissions=[
                            "extras.view_computedfield",
                        ],
                        buttons=(
                            NavMenuAddButton(
                                link="extras:computedfield_add",
                                permissions=[
                                    "extras.add_computedfield",
                                ],
                            ),
                        ),
                    ),
                    NavMenuItem(
                        link="extras:customlink_list",
                        name="Custom Links",
                        label=_("Custom Links"),
                        weight=400,
                        permissions=[
                            "extras.view_customlink",
                        ],
                        buttons=(
                            NavMenuAddButton(
                                link="extras:customlink_add",
                                permissions=[
                                    "extras.add_customlink",
                                ],
                            ),
                        ),
                    ),
                ),
            ),
            NavMenuGroup(
                name="Metadata",
                label=_("Metadata"),
                weight=700,
                items=(
                    NavMenuItem(
                        link="extras:metadatatype_list",
                        name="Metadata Types",
                        label=_("Metadata Types"),
                        weight=100,
                        permissions=[
                            "extras.view_metadatatype",
                        ],
                        buttons=(
                            NavMenuAddButton(
                                link="extras:metadatatype_add",
                                permissions=[
                                    "extras.add_metadatatype",
                                ],
                            ),
                        ),
                    ),
                    NavMenuItem(
                        link="extras:objectmetadata_list",
                        name="Object Metadata",
                        label=_("Object Metadata"),
                        weight=200,
                        permissions=[
                            "extras.view_objectmetadata",
                        ],
                        buttons=(),
                    ),
                ),
            ),
        ),
    ),
    NavMenuTab(
        name="Apps",
        label=_("Apps"),
        icon=NavigationIconChoices.APPS,
        weight=NavigationWeightChoices.APPS,
        groups=(
            NavMenuGroup(
                name="General",
                label=_("General"),
                weight=100,
                items=(
                    NavMenuItem(
                        link="apps:apps_marketplace",
                        name="Apps Marketplace",
                        label=_("Apps Marketplace"),
                        weight=100,
                    ),
                    NavMenuItem(
                        link="apps:apps_list",
                        name="Installed Apps",
                        label=_("Installed Apps"),
                        weight=200,
                    ),
                ),
            ),
        ),
    ),
)
