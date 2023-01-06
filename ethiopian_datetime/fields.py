import warnings
import datetime as _gregoriancalendar
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from ethiocalendar import date as ethdate, datetime as ethdatetime
from ethiocalendar import fromgretoethio

from . import utils
from . import forms


class EthiopianDateField(models.DateField):
    description = "Ethiopian Date Field"

    def formfield(self, **kwargs):
        defaults = {"form_class": forms.EthiopianDateField}
        defaults.update(kwargs)
        defaults["widget"] = forms.EthiopianDateField.widget
        return super(EthiopianDateField, self).formfield(**defaults)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return fromgretoethio(value)

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if value is None:
            return value
        return self.to_python(value).togregorian()

    def to_python(self, value):
        if value is None:
            return value
        if isinstance(value, ethdatetime):
            if settings.USE_TZ and timezone.is_aware(value):
                # Convert aware datetimes to the default time zone
                # before casting them to dates (#17742).
                default_timezone = timezone.get_default_timezone()
                value = timezone.make_naive(value, default_timezone)
            return value.date()
        if isinstance(value, ethdate):
            return value

        try:
            parsed = utils.parse_date(value)
            if parsed is not None:
                return parsed
        except ValueError:
            raise ValidationError(
                self.error_messages["invalid_date"],
                code="invalid_date",
                params={"value": value},
            )
        raise ValidationError(
            self.error_messages["invalid"],
            code="invalid",
            params={"value": value},
        )


class EthiopianDateTimeField(models.DateTimeField):
    description = "Ethiopian DateTime Field"

    def get_internal_type(self):
        return "DateTimeField"

    def formfield(self, **kwargs):
        defaults = {
            "form_class": forms.EthiopianDateTimeField,
            "widget": forms.EthiopianDateTimeField.widget,
        }
        defaults.update(kwargs)
        defaults["widget"] = forms.MinimalSplitDateTimeMultiWidget
        defaults["form_class"] = forms.EthiopianDateTimeField
        return super(EthiopianDateTimeField, self).formfield(**defaults)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return fromgretoethio(value)

    def to_python(self, value):
        if value is None:
            return value
        if isinstance(value, ethdatetime):
            return value
        if isinstance(value, ethdate):
            value = ethdatetime(value.year, value.month, value.day)
            if settings.USE_TZ:
                warnings.warn(
                    "DateTimeField %s.%s received a naive datetime "
                    "(%s) while time zone support is active."
                    % (self.model.__name__, self.name, value),
                    RuntimeWarning,
                )
                default_timezone = timezone.get_default_timezone()
                value = timezone.make_naive(value, default_timezone)
            return value

        try:
            parsed = forms.parse_datetime(value)
            if parsed is not None:
                return parsed
        except ValueError:
            raise ValidationError(
                self.error_messages["invalid_datetime"],
                code="invalid_datetime",
                params={"value": value},
            )

        try:
            parsed = utils.parse_date(value)
            if parsed is not None:
                return ethdatetime(parsed.year, parsed.month, parsed.day)
        except ValueError:
            raise ValidationError(
                self.error_messages["invalid_date"],
                code="invalid_date",
                params={"value": value},
            )

        raise ValidationError(
            self.error_messages["invalid"],
            code="invalid",
            params={"value": value},
        )

    def get_prep_value(self, value):
        if value is None:
            return value
        gdate = value.date().togregorian()
        gtime = _gregoriancalendar.time(
            value.time().hour, value.time().minute, value.time().second
        )
        return _gregoriancalendar.datetime.combine(gdate, gtime)

    def value_to_string(self, obj):
        val = self.value_from_object(obj)
        return "" if val is None else val.isoformat()
