from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils import formats, timezone
from django.core.exceptions import ValidationError
from ethiocalendar import date as ethdate, datetime as ethdatetime, time as ethtime

from .widgets import (
    EthiopianDateInput,
    EthiopianTimeInput,
    MinimalSplitDateTimeMultiWidget,
)

from .utils import parse_datetime


class EthiopianTimeField(forms.TimeField):
    widget = EthiopianTimeInput

    def to_python(self, value):
        """
        Validate that the input can be converted to a time. Return a Python
        datetime.time object.
        """
        if value in self.empty_values:
            return None
        if isinstance(value, ethtime):
            return value

        try:
            hour, minute, second = (int(i) for i in value.split(":"))
            the_time = ethtime(hour=hour, minute=minute, second=second)
        except (ValueError, TypeError):
            raise ValidationError(self.error_messages["invalid"], code="invalid")
        return the_time

    def strptime(self, value, format):
        return ethdatetime.strptime(value, format).time()


class EthiopianDateField(forms.DateField):
    widget = EthiopianDateInput
    input_formats = formats.get_format_lazy("DATE_INPUT_FORMATS")

    def to_python(self, value):
        if value in self.empty_values:
            return None
        if isinstance(value, ethdatetime):
            return value.date()
        if isinstance(value, ethdate):
            return value

        try:
            year, month, day = (int(i) for i in value.split("-"))
            the_date = ethdate(year, month, day)
        except (ValueError, TypeError):
            raise ValidationError(self.error_messages["invalid"], code="invalid")
        return the_date

    def strptime(self, value, format):
        return ethdatetime.strptime(value, format).date()


class EthiopianDateTimeField(forms.SplitDateTimeField):
    widget = MinimalSplitDateTimeMultiWidget
    input_formats = forms.fields.DateTimeFormatsIterator()
    default_error_messages = {
        "invalid_date": _("Enter a valid date."),
        "invalid_time": _("Enter a valid time."),
    }

    def __init__(
        self, input_date_formats=None, input_time_formats=None, *args, **kwargs
    ):
        errors = self.default_error_messages.copy()
        if "error_messages" in kwargs:
            errors.update(kwargs["error_messages"])
        localize = kwargs.get("localize", False)
        fields = (
            EthiopianDateField(
                input_formats=input_date_formats,
                error_messages={"invalid": errors["invalid_time"]},
                localize=localize,
            ),
            EthiopianTimeField(
                input_formats=input_time_formats,
                error_messages={"invalid": errors["invalid_time"]},
                localize=localize,
            ),
        )
        super(forms.SplitDateTimeField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        if data_list:
            if data_list[0] in self.empty_values:
                raise ValidationError(
                    self.error_messages["invalid_date"], code="invalid_date"
                )
            if data_list[1] in self.empty_values:
                raise ValidationError(
                    self.error_messages["invalid_time"], code="invalid_time"
                )
            return ethdatetime.combine(*data_list)
        return None

    def prepare_value(self, value):
        if isinstance(value, ethdatetime):
            value = forms.utils.to_current_timezone(value)
        return value

    def get_db_prep_value(self, value, connection, prepared=False):
        default_timezone = timezone.get_current_timezone()
        if value and timezone.is_naive(value):
            value = timezone.make_aware(value, default_timezone)
        return self.strftime("%Y-%m-%d %H:%M:%S", value.timetuple())

    def strptime(self, value, format):
        return ethdatetime.strptime(value, format).togregorian()

    def to_python(self, value):
        if value in self.empty_values:
            return None
        if isinstance(value, ethdatetime):
            return forms.utils.from_current_timezone(value)
        if isinstance(value, ethdate):
            result = ethdate(value.year, value.month, value.day)
            return forms.utils.from_current_timezone(result)

        try:
            result = parse_datetime(value.strip())
        except ValueError:
            raise ValidationError(self.error_messages["invalid"], code="invalid")
        if not result:
            result = super().to_python(value)

        return forms.utils.from_current_timezone(result)
