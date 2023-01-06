from django import forms


class EthiopianTimeInput(forms.TimeInput):
    def __init__(self, attrs=None, format=None):
        attrs = {"class": "vEthiopianTime vTimeField", "size": "8", **(attrs or {})}
        super().__init__(attrs=attrs, format=format)


class EthiopianDateInput(forms.DateInput):
    template_name = "ethiopian_datetime/ethiopian_date.html"
    format_key = "DATETIME_INPUT_FORMATS"

    class Media:
        css = {
            "all": [
                "ethiopian_datetime/css/redmond.calendars.picker.css",
            ],
        }
        js = (
            "ethiopian_datetime/js/jquery.min.js",
            "ethiopian_datetime/js/jquery.plugin.js",
            "ethiopian_datetime/js/jquery.calendars.js",
            "ethiopian_datetime/js/jquery.calendars.plus.js",
            "ethiopian_datetime/js/jquery.calendars.picker.js",
            "ethiopian_datetime/js/jquery.calendars.ethiopian.js",
            "ethiopian_datetime/js/jquery.calendars.ethiopian-am.js",
            "ethiopian_datetime/js/calendar_init.js",
        )

    def __init__(self, attrs=None, format=None):
        final_attrs = {"class": "vEthiopianDate"}
        if attrs is not None:
            final_attrs.update(attrs)
        super().__init__(attrs=final_attrs, format=format)


class MinimalSplitDateTimeMultiWidget(forms.MultiWidget):
    template_name = (
        "ethiopian_datetime/ethiopian_split_datetime.html"  # for django >= 1.11
    )

    def __init__(self, widgets=None, attrs=None):
        if widgets is None:
            if attrs is None:
                attrs = {}
            date_attrs = attrs.copy()
            time_attrs = attrs.copy()

            widgets = [
                EthiopianDateInput(attrs=date_attrs),
                EthiopianTimeInput(attrs=time_attrs),
            ]
        forms.MultiWidget.__init__(self, widgets, attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["date_label"] = "Date:"
        context["time_label"] = "Time:"
        return context

    def decompress(self, value):
        if value:
            value = forms.utils.to_current_timezone(value)
            return [value.date(), value.time().replace(microsecond=0)]
        return [None, None]

    def value_from_datadict(self, data, files, name):
        date_str, time_str = super().value_from_datadict(data, files, name)

        if date_str == time_str == "":
            return [None, None]

        if time_str == "":
            time_str = "00:00:00"

        return (date_str, time_str)
