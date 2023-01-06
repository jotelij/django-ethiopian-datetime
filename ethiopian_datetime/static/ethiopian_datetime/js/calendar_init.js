$(function () {
	var calendar = $.calendars.instance('ethiopian', 'am');
	$('.vEthiopianDate').calendarsPicker({calendar: calendar});
});