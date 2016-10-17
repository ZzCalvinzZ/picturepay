$(function () {
	if ($(window).width() > 752) {
		$(window).stuck();
	}

	if ($('.errorlist').length > 0) {
		$('.open-reveal-form').click();
	}
});

