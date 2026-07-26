from celery import states
from django.utils.translation import gettext_lazy as _

from nautobot.core.choices import ChoiceSet

#
# Approval Workflows
#


class ApprovalWorkflowStateChoices(ChoiceSet):
    """
    Choices for:
    1. current_state field on the ApprovalWorkflow model.
    2. state field on the ApprovalWorkflowStage model.
    3. state field on the ApprovalWorkflowStageResponse model.
    """

    PENDING = "Pending"
    APPROVED = "Approved"
    DENIED = "Denied"
    CANCELED = "Canceled"
    COMMENT = "Comment"

    CHOICES = (
        (PENDING, _("Pending")),
        (APPROVED, _("Approved")),
        (DENIED, _("Denied")),
        (CANCELED, _("Canceled")),
        (COMMENT, _("Comment")),
    )
    CSS_CLASSES = {
        PENDING: "info",
        APPROVED: "success",
        DENIED: "danger",
        CANCELED: "warning",
        COMMENT: "info",
    }


#
# Banners (currently plugin-specific)
#


class BannerClassChoices(ChoiceSet):
    """Styling choices for custom banners."""

    CLASS_SUCCESS = "success"
    CLASS_INFO = "info"
    CLASS_WARNING = "warning"
    CLASS_DANGER = "danger"

    CHOICES = (
        (CLASS_SUCCESS, _("Success")),
        (CLASS_INFO, _("Info")),
        (CLASS_WARNING, _("Warning")),
        (CLASS_DANGER, _("Danger")),
    )


#
# Contact Association
#


class ContactAssociationRoleChoices(ChoiceSet):
    """Role choices for contact association instances"""

    ROLE_ADMINISTRATIVE = "administrative"
    ROLE_BILLING = "billing"
    ROLE_SUPPORT = "support"
    ROLE_ON_SITE = "on site"

    CHOICES = (
        (ROLE_ADMINISTRATIVE, _("Administrative")),
        (ROLE_BILLING, _("Billing")),
        (ROLE_SUPPORT, _("Support")),
        (ROLE_ON_SITE, _("On Site")),
    )


class ContactAssociationStatusChoices(ChoiceSet):
    """Status choices for contact association instances"""

    STATUS_PRIMARY = "primary"
    STATUS_SECONDARY = "secondary"
    STATUS_ACTIVE = "active"

    CHOICES = (
        (STATUS_PRIMARY, _("Primary")),
        (STATUS_SECONDARY, _("Secondary")),
        (STATUS_ACTIVE, _("Active")),
    )


#
# CustomFields
#


class CustomFieldFilterLogicChoices(ChoiceSet):
    FILTER_DISABLED = "disabled"
    FILTER_LOOSE = "loose"
    FILTER_EXACT = "exact"

    CHOICES = (
        (FILTER_DISABLED, _("Disabled")),
        (FILTER_LOOSE, _("Loose")),
        (FILTER_EXACT, _("Exact")),
    )


class CustomFieldTypeChoices(ChoiceSet):
    TYPE_TEXT = "text"
    TYPE_INTEGER = "integer"
    TYPE_BOOLEAN = "boolean"
    TYPE_DATE = "date"
    TYPE_URL = "url"
    TYPE_SELECT = "select"
    TYPE_MULTISELECT = "multi-select"
    TYPE_JSON = "json"
    TYPE_MARKDOWN = "markdown"
    TYPE_DATETIME = "datetime"

    CHOICES = (
        (TYPE_TEXT, _("Text")),
        (TYPE_INTEGER, _("Integer")),
        (TYPE_BOOLEAN, _("Boolean (true/false)")),
        (TYPE_DATE, _("Date")),
        (TYPE_DATETIME, _("Date/time")),
        (TYPE_URL, _("URL")),
        (TYPE_SELECT, _("Selection")),
        (TYPE_MULTISELECT, _("Multiple selection")),
        (TYPE_JSON, _("JSON")),
        (TYPE_MARKDOWN, _("Markdown")),
    )

    # Types that support validation_minimum/validation_maximum
    MIN_MAX_TYPES = (
        TYPE_TEXT,
        TYPE_INTEGER,
        TYPE_URL,
        TYPE_SELECT,
        TYPE_MULTISELECT,
        TYPE_JSON,
        TYPE_MARKDOWN,
    )

    # Types that support validation_regex
    REGEX_TYPES = (
        TYPE_TEXT,
        TYPE_URL,
        TYPE_SELECT,
        TYPE_MULTISELECT,
        TYPE_JSON,
        TYPE_MARKDOWN,
    )


class ComputedFieldTypeChoices(ChoiceSet):
    TYPE_TEXT = "text"
    TYPE_MARKDOWN = "markdown"

    CHOICES = (
        (TYPE_TEXT, _("Text")),
        (TYPE_MARKDOWN, _("Markdown")),
    )


#
# Button Classes
#


class ButtonClassChoices(ChoiceSet):
    CLASS_DEFAULT = "default"  # maps to "secondary" in v3 UI, but kept for backwards compatibility
    CLASS_PRIMARY = "primary"
    CLASS_SUCCESS = "success"
    CLASS_INFO = "info"
    CLASS_WARNING = "warning"
    CLASS_DANGER = "danger"
    CLASS_LINK = "link"

    CHOICES = (
        (CLASS_DEFAULT, _("Default")),
        (CLASS_PRIMARY, _("Primary (blue)")),
        (CLASS_SUCCESS, _("Success (green)")),
        (CLASS_INFO, _("Info (blue)")),
        (CLASS_WARNING, _("Warning (orange)")),
        (CLASS_DANGER, _("Danger (red)")),
        (CLASS_LINK, _("None (link)")),
    )


#
# Dynamic Groups
#


class DynamicGroupTypeChoices(ChoiceSet):
    TYPE_DYNAMIC_FILTER = "dynamic-filter"
    TYPE_DYNAMIC_SET = "dynamic-set"
    TYPE_STATIC = "static"

    CHOICES = (
        (TYPE_DYNAMIC_FILTER, _("Filter-defined")),
        (TYPE_DYNAMIC_SET, _("Group of groups")),
        (TYPE_STATIC, _("Static assignment")),
    )


class DynamicGroupOperatorChoices(ChoiceSet):
    OPERATOR_UNION = "union"
    OPERATOR_INTERSECTION = "intersection"
    OPERATOR_DIFFERENCE = "difference"

    CHOICES = (
        (OPERATOR_UNION, _("Include (OR)")),
        (OPERATOR_INTERSECTION, _("Restrict (AND)")),
        (OPERATOR_DIFFERENCE, _("Exclude (NOT)")),
    )


#
# Jobs
#


class JobExecutionType(ChoiceSet):
    TYPE_IMMEDIATELY = "immediately"
    TYPE_FUTURE = "future"
    TYPE_HOURLY = "hourly"
    TYPE_DAILY = "daily"
    TYPE_WEEKLY = "weekly"
    TYPE_CUSTOM = "custom"

    CHOICES = (
        (TYPE_IMMEDIATELY, _("Once immediately")),
        (TYPE_FUTURE, _("Once in the future")),
        (TYPE_HOURLY, _("Recurring hourly")),
        (TYPE_DAILY, _("Recurring daily")),
        (TYPE_WEEKLY, _("Recurring weekly")),
        (TYPE_CUSTOM, _("Recurring custom")),
    )

    SCHEDULE_CHOICES = (
        TYPE_FUTURE,
        TYPE_HOURLY,
        TYPE_DAILY,
        TYPE_WEEKLY,
        TYPE_CUSTOM,
    )

    RECURRING_CHOICES = (
        TYPE_HOURLY,
        TYPE_DAILY,
        TYPE_WEEKLY,
        TYPE_CUSTOM,
    )

    CELERY_INTERVAL_MAP = {
        TYPE_HOURLY: "hours",
        TYPE_DAILY: "days",
        TYPE_WEEKLY: "days",  # a week is expressed as 7 days
    }


class JobQueueTypeChoices(ChoiceSet):
    TYPE_CELERY = "celery"
    TYPE_KUBERNETES = "kubernetes"

    CHOICES = (
        (TYPE_CELERY, _("Celery")),
        (TYPE_KUBERNETES, _("Kubernetes")),
    )


#
# Job results
#


class JobResultStatusChoices(ChoiceSet):
    """
    These status choices are using the same taxonomy as within Celery core. A Nautobot Job status
    is equivalent to a Celery task state.
    """

    STATUS_FAILURE = states.FAILURE
    STATUS_IGNORED = states.IGNORED
    STATUS_PENDING = states.PENDING
    STATUS_RECEIVED = states.RECEIVED
    STATUS_REJECTED = states.REJECTED
    STATUS_RETRY = states.RETRY
    STATUS_REVOKED = states.REVOKED
    STATUS_STARTED = states.STARTED
    STATUS_SUCCESS = states.SUCCESS

    CHOICES = sorted(zip(states.ALL_STATES, states.ALL_STATES))

    #: Set of all possible states.
    ALL_STATES = states.ALL_STATES
    #: Set of states meaning the task returned an exception.
    # {RETRY, FAILURE, REVOKED}
    EXCEPTION_STATES = states.EXCEPTION_STATES
    #: State precedence.
    #: None represents the precedence of an unknown state.
    #: Lower index means higher precedence.
    # [SUCCESS, FAILURE, None, REVOKED, STARTED, RECEIVED, REJECTED, RETRY, PENDING]
    PRECEDENCE = states.PRECEDENCE
    #: Set of exception states that should propagate exceptions to the user.
    # {FAILURE, REVOKED}
    PROPAGATE_STATES = states.PROPAGATE_STATES
    #: Set of states meaning the task result is ready (has been executed).
    # {SUCCESS, FAILURE, REVOKED}
    READY_STATES = states.READY_STATES
    #: Set of states meaning the task result is not ready (hasn't been executed).
    # {PENDING, RECEIVED, STARTED, REJECTED, RETRY}
    UNREADY_STATES = states.UNREADY_STATES

    @staticmethod
    def precedence(state):
        """
        Get the precedence for a state. Lower index means higher precedence.

        Args:
            state (str): One of the status choices.

        Returns:
            (int): Precedence value.

        Examples:
            >>> JobResultStatusChoices.precedence(JobResultStatusChoices.STATUS_SUCCESS)
            0

        """
        return states.precedence(state)


#
# Log Levels for Jobs (formerly Reports and Custom Scripts)
#


class LogLevelChoices(ChoiceSet):
    LOG_DEBUG = "debug"
    LOG_INFO = "info"
    LOG_SUCCESS = "success"
    LOG_WARNING = "warning"
    LOG_FAILURE = "failure"
    LOG_ERROR = "error"
    LOG_CRITICAL = "critical"

    CHOICES = (
        (LOG_DEBUG, _("Debug")),
        (LOG_INFO, _("Info")),
        (LOG_SUCCESS, _("Success")),
        (LOG_WARNING, _("Warning")),
        (LOG_FAILURE, _("Failure")),
        (LOG_ERROR, _("Error")),
        (LOG_CRITICAL, _("Critical")),
    )

    CSS_CLASSES = {
        LOG_DEBUG: "debug",
        LOG_INFO: "info",
        LOG_SUCCESS: "success",
        LOG_WARNING: "warning",
        LOG_FAILURE: "failure",
        LOG_ERROR: "error",
        LOG_CRITICAL: "critical",
    }


#
# JobConsoleEntry
#


class JobConsoleEntryOutputTypeChoices(ChoiceSet):
    TYPE_OUTPUT = "output"
    TYPE_STDOUT = "stdout"
    TYPE_STDERR = "stderr"

    CHOICES = (
        (TYPE_OUTPUT, _("Output")),
        (TYPE_STDOUT, _("Standard output")),
        (TYPE_STDERR, _("Standard error")),
    )


#
# JobCancelType
#


class JobCancelTypeChoices(ChoiceSet):
    TYPE_TERMINATED = "terminated"
    TYPE_REAPED = "reaped"
    TYPE_ABANDONED = "abandoned"

    CHOICES = (
        (TYPE_TERMINATED, _("Terminated")),
        (TYPE_REAPED, _("Reaped")),
        (TYPE_ABANDONED, _("Abandoned")),
    )


#
# ScheduledJob
#


class ScheduledJobStateChoices(ChoiceSet):
    ACTIVE = "active"
    PENDING = "pending"
    DENIED = "denied"
    CANCELED = "canceled"
    COMPLETED = "completed"
    ERRORED = "errored"

    CHOICES = (
        (ACTIVE, _("Active")),
        (PENDING, _("Pending Approval")),
        (DENIED, _("Approval Denied")),
        (CANCELED, _("Approval Canceled")),
        (COMPLETED, _("Completed")),
        (ERRORED, _("Errored")),
    )


#
# Metadata
#


class MetadataTypeDataTypeChoices(CustomFieldTypeChoices):
    """
    Values for the MetadataType.data_type field.

    Generally equivalent to CustomFieldTypeChoices, but adds TYPE_CONTACT_OR_TEAM.
    """

    TYPE_CONTACT_TEAM = "contact-or-team"
    # TODO: these should be migrated to CustomFieldTypeChoices and support added in CustomField data
    TYPE_FLOAT = "float"

    CHOICES = (
        *CustomFieldTypeChoices.CHOICES,
        (TYPE_CONTACT_TEAM, _("Contact or Team")),
        # TODO: these should be migrated to CustomFieldTypeChoices and support added in CustomField data
        (TYPE_FLOAT, _("Floating point number")),
    )

    MIN_MAX_TYPES = (
        *CustomFieldTypeChoices.MIN_MAX_TYPES,
        TYPE_FLOAT,
    )


#
# ObjectChanges
#


class ObjectChangeActionChoices(ChoiceSet):
    ACTION_CREATE = "create"
    ACTION_UPDATE = "update"
    ACTION_DELETE = "delete"

    CHOICES = (
        (ACTION_CREATE, _("Created")),
        (ACTION_UPDATE, _("Updated")),
        (ACTION_DELETE, _("Deleted")),
    )

    CSS_CLASSES = {
        ACTION_CREATE: "success",
        ACTION_UPDATE: "primary",
        ACTION_DELETE: "danger",
    }


class ObjectChangeEventContextChoices(ChoiceSet):
    CONTEXT_WEB = "web"
    CONTEXT_JOB = "job"
    CONTEXT_JOB_HOOK = "job-hook"
    CONTEXT_ORM = "orm"
    CONTEXT_UNKNOWN = "unknown"

    CHOICES = (
        (CONTEXT_WEB, _("Web")),
        (CONTEXT_JOB, _("Job")),
        (CONTEXT_JOB_HOOK, _("Job hook")),
        (CONTEXT_ORM, _("ORM")),
        (CONTEXT_UNKNOWN, _("Unknown")),
    )


#
# Relationships
#


class RelationshipRequiredSideChoices(ChoiceSet):
    NEITHER_SIDE_REQUIRED = ""
    SOURCE_SIDE_REQUIRED = "source"
    DESTINATION_SIDE_REQUIRED = "destination"

    CHOICES = (
        (NEITHER_SIDE_REQUIRED, _("Neither side required")),
        (SOURCE_SIDE_REQUIRED, _("Source objects MUST implement this relationship")),
        (DESTINATION_SIDE_REQUIRED, _("Destination objects MUST implement this relationship")),
    )


class RelationshipSideChoices(ChoiceSet):
    SIDE_SOURCE = "source"
    SIDE_DESTINATION = "destination"
    SIDE_PEER = "peer"  # for symmetric / non-directional relationships

    CHOICES = (
        (SIDE_SOURCE, _("Source")),
        (SIDE_DESTINATION, _("Destination")),
        (SIDE_PEER, _("Peer")),
    )

    OPPOSITE = {
        SIDE_SOURCE: SIDE_DESTINATION,
        SIDE_DESTINATION: SIDE_SOURCE,
        SIDE_PEER: SIDE_PEER,
    }


class RelationshipTypeChoices(ChoiceSet):
    TYPE_ONE_TO_ONE = "one-to-one"
    TYPE_ONE_TO_ONE_SYMMETRIC = "symmetric-one-to-one"
    TYPE_ONE_TO_MANY = "one-to-many"
    TYPE_MANY_TO_MANY = "many-to-many"
    TYPE_MANY_TO_MANY_SYMMETRIC = "symmetric-many-to-many"

    CHOICES = (
        (TYPE_ONE_TO_ONE, _("One to One")),
        (TYPE_ONE_TO_ONE_SYMMETRIC, _("Symmetric One to One")),
        (TYPE_ONE_TO_MANY, _("One to Many")),
        (TYPE_MANY_TO_MANY, _("Many to Many")),
        (TYPE_MANY_TO_MANY_SYMMETRIC, _("Symmetric Many to Many")),
    )


#
# Secrets
#


class SecretsGroupAccessTypeChoices(ChoiceSet):
    TYPE_GENERIC = "Generic"

    TYPE_CONSOLE = "Console"
    TYPE_GNMI = "gNMI"
    TYPE_HTTP = "HTTP(S)"
    TYPE_NETCONF = "NETCONF"
    TYPE_REST = "REST"
    TYPE_RESTCONF = "RESTCONF"
    TYPE_SNMP = "SNMP"
    TYPE_SSH = "SSH"

    CHOICES = (
        (TYPE_GENERIC, "Generic"),
        (TYPE_CONSOLE, "Console"),
        (TYPE_GNMI, "gNMI"),
        (TYPE_HTTP, "HTTP(S)"),
        (TYPE_NETCONF, "NETCONF"),
        (TYPE_REST, "REST"),
        (TYPE_RESTCONF, "RESTCONF"),
        (TYPE_SNMP, "SNMP"),
        (TYPE_SSH, "SSH"),
    )


class SecretsGroupSecretTypeChoices(ChoiceSet):
    TYPE_AUTHKEY = "authentication-key"
    TYPE_AUTHPROTOCOL = "authentication-protocol"
    TYPE_KEY = "key"
    TYPE_NOTES = "notes"
    TYPE_PASSWORD = "password"  # noqa: S105  # hardcoded-password-string -- false positive
    TYPE_PRIVALGORITHM = "private-algorithm"
    TYPE_PRIVKEY = "private-key"
    TYPE_SECRET = "secret"  # noqa: S105  # hardcoded-password-string -- false positive
    TYPE_TOKEN = "token"  # noqa: S105  # hardcoded-password-string -- false positive
    TYPE_URL = "url"
    TYPE_USERNAME = "username"

    CHOICES = (
        (TYPE_AUTHKEY, _("Authentication Key")),
        (TYPE_AUTHPROTOCOL, _("Authentication Protocol")),
        (TYPE_KEY, _("Key")),
        (TYPE_NOTES, _("Notes")),
        (TYPE_PASSWORD, _("Password")),
        (TYPE_PRIVALGORITHM, _("Private Algorithm")),
        (TYPE_PRIVKEY, _("Private Key")),
        (TYPE_SECRET, _("Secret")),
        (TYPE_TOKEN, _("Token")),
        (TYPE_URL, _("URL")),
        (TYPE_USERNAME, _("Username")),
    )


#
# Webhooks
#


class WebhookHttpMethodChoices(ChoiceSet):
    METHOD_GET = "GET"
    METHOD_POST = "POST"
    METHOD_PUT = "PUT"
    METHOD_PATCH = "PATCH"
    METHOD_DELETE = "DELETE"

    CHOICES = (
        (METHOD_GET, "GET"),
        (METHOD_POST, "POST"),
        (METHOD_PUT, "PUT"),
        (METHOD_PATCH, "PATCH"),
        (METHOD_DELETE, "DELETE"),
    )
