from django import forms
from django.conf import settings
from django.contrib.auth.forms import (
    AdminPasswordChangeForm as _AdminPasswordChangeForm,
    AuthenticationForm,
    PasswordChangeForm as DjangoPasswordChangeForm,
)
from django.utils.translation import gettext_lazy as _
from timezone_field import TimeZoneFormField

from nautobot.core.events import publish_event
from nautobot.core.forms import BootstrapMixin, DateTimePicker
from nautobot.core.forms.widgets import StaticSelect2
from nautobot.core.utils.config import get_settings_or_config
from nautobot.users.utils import serialize_user_without_config_and_views

from .models import Token


class LoginForm(BootstrapMixin, AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].widget.attrs["placeholder"] = ""
        self.fields["password"].widget.attrs["placeholder"] = ""


class PasswordChangeForm(BootstrapMixin, DjangoPasswordChangeForm):
    pass


class TokenForm(BootstrapMixin, forms.ModelForm):
    key = forms.CharField(
        required=False,
        help_text=_("If no key is provided, one will be generated automatically."),
    )

    class Meta:
        model = Token
        fields = [
            "key",
            "write_enabled",
            "expires",
            "description",
        ]
        widgets = {
            "expires": DateTimePicker(),
        }


class AdvancedProfileSettingsForm(BootstrapMixin, forms.Form):
    request_profiling = forms.BooleanField(
        required=False,
        help_text=_(
            "Enable request profiling for the duration of the login session. "
            "This is for debugging purposes and should only be enabled when "
            "instructed by an administrator."
        ),
        label=_("Request profiling"),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ALLOW_REQUEST_PROFILING is a constance config option that controls whether users can enable request profiling
        ALLOW_REQUEST_PROFILING = get_settings_or_config("ALLOW_REQUEST_PROFILING")
        if not ALLOW_REQUEST_PROFILING:
            self.fields["request_profiling"].disabled = True

    def clean(self):
        # ALLOW_REQUEST_PROFILING is a constance config option that controls whether users can enable request profiling
        ALLOW_REQUEST_PROFILING = get_settings_or_config("ALLOW_REQUEST_PROFILING")
        if not ALLOW_REQUEST_PROFILING and self.cleaned_data["request_profiling"]:
            raise forms.ValidationError(
                {"request_profiling": _("Request profiling has been globally disabled by an administrator.")}
            )


def _language_choices():
    """
    Selectable languages, with a blank choice meaning "whatever this Nautobot instance defaults to".

    Evaluated per-render rather than at import so that an operator narrowing `LANGUAGES` takes effect
    without a code change, and so tests can override the setting.
    """
    return [("", "Use this Nautobot instance's default language"), *settings.LANGUAGES]


class PreferenceProfileSettingsForm(BootstrapMixin, forms.Form):
    timezone = TimeZoneFormField(
        required=False,
        label=_("Timezone"),
        help_text=_("Set your preferred timezone."),
        widget=StaticSelect2,
    )
    language = forms.ChoiceField(
        required=False,
        label=_("Language"),
        choices=_language_choices,
        help_text=(
            _(
                "Set your preferred language for the Nautobot user interface. This affects only your own sessions. "
                "Translations other than English are machine-assisted and pending native-speaker review; anything not "
                "yet translated is shown in English."
            )
        ),
        widget=StaticSelect2,
    )


class NavbarFavoritesAddForm(forms.Form):
    link = forms.CharField(label=_("Link"))
    name = forms.CharField(label=_("Name"))
    tab_name = forms.CharField(label=_("Tab name"))


class NavbarFavoritesRemoveForm(forms.Form):
    link = forms.CharField(label=_("Link"))


class AdminPasswordChangeForm(_AdminPasswordChangeForm):
    def save(self, commit=True):
        # Override `_AdminPasswordChangeForm.save()` to publish admin change user password event
        instance = super().save(commit)
        if commit:
            payload = serialize_user_without_config_and_views(instance)
            publish_event(topic="nautobot.admin.user.change_password", payload=payload)
        return instance
