$(function () {
	$('#id_number').hide();

	if ($(window).width() > 752) {
		$(window).stuck();
	}

	if ($('.errorlist').length > 0) {
		$('.open-reveal-form').click();
	}

	$('#line-unveil-form input[name=number_preset]').on('click', function () {
		if ($('#id_number_preset_3').is(':checked')) {
			$('#id_number').show();
		} else {
			$('#id_number').hide();
		}

	});
});

