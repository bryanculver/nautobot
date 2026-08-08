import re

from django.conf import settings
from django.core.checks import Error, register, Tags, Warning  # pylint: disable=redefined-builtin
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import connections

from nautobot.core.utils.config import get_settings_or_config
from nautobot.dcim.choices import DeviceUniquenessChoices

E002 = Error(
    "'nautobot.core.authentication.ObjectPermissionBackend' must be included in AUTHENTICATION_BACKENDS",
    id="nautobot.core.E002",
    obj=settings,
)

E003 = Error(
    "RELEASE_CHECK_TIMEOUT must be at least 3600 seconds (1 hour)",
    id="nautobot.core.E003",
    obj=settings,
)

E004 = Error(
    "RELEASE_CHECK_URL must be a valid API URL. Example: https://api.github.com/repos/nautobot/nautobot",
    id="nautobot.core.E004",
    obj=settings,
)

E005 = Error(
    "MAINTENANCE_MODE has been set but SESSION_ENGINE is still using the database.  Nautobot can not enter Maintenance mode.",
    id="nautobot.core.E005",
    obj=settings,
)

E006 = Error(
    "The Data Validation Engine app has been moved directly into Nautobot Core.  Please remove 'nautobot_data_validation_engine' from PLUGINS and PLUGINS_CONFIG in your nautobot_config.py.  After running Nautobot migrations successfully, you can then also uninstall 'nautobot-data-validation-engine' from the Python environment.",
    id="nautobot.core.E006",
    obj=settings,
)

# E007 and E008 are dynamically constructed inline below

E009 = Error(
    "You appear to have overridden settings.STORAGES incorrectly. "
    "In addition to the Django standard keys of 'default' and 'staticfiles', "
    "Nautobot also requires the key 'nautobotjobfiles' to define storage configuration for Job input/output files.",
    hint='Nautobot defaults to setting STORAGES["nautobotjobfiles"]["BACKEND"] to '
    '"db_file_storage.storage.DatabaseFileStorage", but in many cases you should override this. '
    "Refer to https://docs.nautobot.com/projects/core/en/stable/user-guide/administration/configuration/settings/#storages for guidance.",
    id="nautobot.core.E009",
    obj=settings,
)

# E010 is dynamically constructed inline below

# W005 was removed in v3.1.

W006 = Warning(
    "The deprecated setting DEVICE_NAME_AS_NATURAL_KEY is still defined.",
    hint="This setting has been superseded by DEVICE_UNIQUENESS (see Device Constraints).",
    id="nautobot.core.W006",
    obj=settings,
)

W007 = Warning(
    "Invalid DEVICE_UNIQUENESS configuration value.",
    hint=f"DEVICE_UNIQUENESS must be one of: {', '.join(DeviceUniquenessChoices.values())}.",
    id="nautobot.core.W007",
)

# W008 was removed in v3.1.

MIN_POSTGRESQL_MAJOR_VERSION = 14
MIN_POSTGRESQL_MINOR_VERSION = 0

MIN_POSTGRESQL_VERSION = MIN_POSTGRESQL_MAJOR_VERSION * 10000 + MIN_POSTGRESQL_MINOR_VERSION


@register(Tags.security)
def check_object_permissions_backend(app_configs, **kwargs):
    if "nautobot.core.authentication.ObjectPermissionBackend" not in settings.AUTHENTICATION_BACKENDS:
        return [E002]
    return []


@register(Tags.compatibility)
def check_release_check_timeout(app_configs, **kwargs):
    if hasattr(settings, "RELEASE_CHECK_TIMEOUT") and settings.RELEASE_CHECK_TIMEOUT < 3600:
        return [E003]
    return []


@register(Tags.compatibility)
def check_release_check_url(app_configs, **kwargs):
    validator = URLValidator()
    if hasattr(settings, "RELEASE_CHECK_URL") and settings.RELEASE_CHECK_URL:
        try:
            validator(settings.RELEASE_CHECK_URL)
        except ValidationError:
            return [E004]
    return []


@register(Tags.compatibility)
def check_maintenance_mode(app_configs, **kwargs):
    if settings.MAINTENANCE_MODE and settings.SESSION_ENGINE == "django.contrib.sessions.backends.db":
        return [E005]
    return []


@register(Tags.database)
def check_postgresql_version(app_configs, databases=None, **kwargs):
    if databases is None:
        return []
    errors = []
    for alias in databases:
        conn = connections[alias]
        if conn.vendor == "postgresql":
            server_version = conn.cursor().connection.info.server_version
            if server_version < MIN_POSTGRESQL_VERSION:
                errors.append(
                    Error(
                        f"PostgreSQL version less than {MIN_POSTGRESQL_VERSION} "
                        f"(i.e. {MIN_POSTGRESQL_MAJOR_VERSION}.{MIN_POSTGRESQL_MINOR_VERSION}) "
                        "is not supported by this version of Nautobot",
                        id="nautobot.core.E006",
                        obj=f"connections[{alias}]",
                        hint=f"Detected version is {server_version} (major version {server_version // 10000})",
                    )
                )

    return errors


@register(Tags.security)
def check_sanitizer_patterns(app_configs, **kwargs):
    errors = []
    for entry in settings.SANITIZER_PATTERNS:
        if (
            not isinstance(entry, (tuple, list))
            or len(entry) != 2
            or not isinstance(entry[0], re.Pattern)
            or not isinstance(entry[1], str)
        ):
            errors.append(
                Error(
                    "Invalid entry in settings.SANITIZER_PATTERNS",
                    hint="Each entry must be a list or tuple of (compiled regexp, replacement string)",
                    obj=entry,
                    id="nautobot.core.E007",
                )
            )
            continue

        sanitizer, repl = entry
        try:
            sanitizer.sub(repl.format(replacement="(REDACTED)"), "Hello world!")
        except re.error as exc:
            errors.append(
                Error(
                    "Entry in settings.SANITIZER_PATTERNS not usable for sanitization",
                    hint=str(exc),
                    obj=entry,
                    id="nautobot.core.E008",
                )
            )

    return errors


@register(Tags.compatibility)
def check_data_validation_engine_installed(app_configs, **kwargs):
    app_name = "nautobot_data_validation_engine"
    if app_name in settings.PLUGINS or app_name in settings.PLUGINS_CONFIG:
        return [E006]
    return []


@register(Tags.compatibility)
def check_storages_includes_nautobotjobfiles(app_configs, **kwargs):
    if "nautobotjobfiles" not in settings.STORAGES:
        return [E009]
    return []


@register(Tags.compatibility)
def check_deprecated_device_name_as_natural_key(app_configs, **kwargs):
    """
    Warn if the deprecated DEVICE_NAME_AS_NATURAL_KEY setting is still defined.

    This setting existed prior to 3.0 and has been replaced by the
    DEVICE_UNIQUENESS Constance configuration.
    """
    try:
        get_settings_or_config("DEVICE_NAME_AS_NATURAL_KEY")
        return [W006]
    except AttributeError:
        pass
    return []


@register(Tags.compatibility)
def check_valid_value_for_device_uniqueness(app_configs, **kwargs):
    """
    Warn if the invalid value for DEVICE_UNIQUENESS is set.
    """
    try:
        device_uniqueness = get_settings_or_config("DEVICE_UNIQUENESS")
        if device_uniqueness not in DeviceUniquenessChoices.values():
            return [W007]
    except AttributeError:
        return [W007]
    return []


@register(Tags.compatibility)
def check_for_removed_storage_settings(app_configs, **kwargs):
    """Warn if any removed storage settings are set."""
    errors = []
    for setting_name, replacement in [
        ("DEFAULT_FILE_STORAGE", 'STORAGES["default"]["BACKEND"]'),
        ("JOB_FILE_IO_STORAGE", 'STORAGES["nautobotjobfiles"]["BACKEND"]'),
        ("STATICFILES_STORAGE", 'STORAGES["staticfiles"]["BACKEND"]'),
        ("STORAGE_CONFIG", 'STORAGES[...]["OPTIONS"]'),
        ("STORAGE_BACKEND", 'STORAGES["default"]["BACKEND"]'),
    ]:
        if settings.is_overridden(setting_name):
            errors.append(
                Error(
                    msg=f"The setting {setting_name} is no longer supported in Nautobot 3.1 and later.",
                    hint=f"You must migrate to setting {replacement} instead. Refer to "
                    "https://docs.nautobot.com/projects/core/en/stable/user-guide/administration/configuration/settings/#storages for guidance.",
                    obj=settings,
                    id="nautobot.core.E010",
                )
            )

    return errors


@register(Tags.database)
def check_database_unicode_support(app_configs, databases=None, **kwargs):
    """
    Verify that the database itself can actually store the full range of Unicode.

    Nautobot asks MySQL for a `utf8mb4` *connection*, and MySQL will happily grant it against a
    database whose own character set is `utf8mb3`. Nothing fails until someone saves a 4-byte
    character -- an emoji, or a CJK Extension B ideograph -- at which point the INSERT raises and
    the user gets a 500 with no indication of the real cause. Failing loudly at startup is far
    cheaper than diagnosing that from a stack trace.

    PostgreSQL is checked for a UTF8 server encoding, which is the equivalent misconfiguration.
    """
    if databases is None:
        return []

    errors = []
    for alias in databases:
        conn = connections[alias]

        if conn.vendor == "mysql":
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT DEFAULT_CHARACTER_SET_NAME, DEFAULT_COLLATION_NAME "
                    "FROM information_schema.SCHEMATA WHERE SCHEMA_NAME = DATABASE()"
                )
                row = cursor.fetchone()
            if row is None:
                continue
            charset, collation = row
            if charset != "utf8mb4":
                errors.append(
                    Error(
                        f"Database '{conn.settings_dict['NAME']}' uses the character set '{charset}', "
                        "which cannot store 4-byte UTF-8 characters such as emoji or less common CJK "
                        "ideographs. Saving such a value will fail at write time.",
                        hint=(
                            f"Convert the database and its existing tables to utf8mb4, for example: "
                            f"ALTER DATABASE `{conn.settings_dict['NAME']}` CHARACTER SET utf8mb4 "
                            f"COLLATE utf8mb4_0900_ai_ci; followed by "
                            f"ALTER TABLE <table> CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci; "
                            f"for each existing table. Detected collation is '{collation}'."
                        ),
                        obj=f"connections[{alias}]",
                        id="nautobot.core.E011",
                    )
                )

        elif conn.vendor == "postgresql":
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT pg_encoding_to_char(encoding) FROM pg_database WHERE datname = current_database()"
                )
                row = cursor.fetchone()
            if row is None:
                continue
            encoding = row[0]
            if encoding != "UTF8":
                errors.append(
                    Error(
                        f"Database '{conn.settings_dict['NAME']}' uses the encoding '{encoding}' rather than UTF8. "
                        "Nautobot requires a UTF8 database to store international text.",
                        hint=(
                            "A database's encoding cannot be changed in place; it must be recreated with "
                            "CREATE DATABASE ... ENCODING 'UTF8' and the data reloaded."
                        ),
                        obj=f"connections[{alias}]",
                        id="nautobot.core.E011",
                    )
                )

    return errors
