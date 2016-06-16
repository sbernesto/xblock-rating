/* Javascript for ratingXBlock. */
// Work-around so we can log in edx-platform, but not fail in Workbench
if (typeof Logger === 'undefined') {
	var Logger = {
		log: function(a, b) { 
			console.log("<<Log>>"); 
			console.log(a);
			console.log(b);
			console.log("<</Log>>"); 
		}
	};
}
function RatingXBlock(runtime, element) {
	var feedback_handler = runtime.handlerUrl(element, 'feedback');
	$(".rating .submit", element).click(function(eventObject) {
		var text = $(".rating .textarea", element).val();
		var rating = -1;
		if ($(".rating_radio:checked", element).length > 0) {
			rating = parseInt($(".rating_radio:checked", element).attr("id").split("_")[1]);
		}
		var feedback = {};
		if(rating > -1) feedback['rating'] = rating;
		if(text) feedback['text'] = text;
		Logger.log("edx.ratingxblock.submit", feedback);

		$.ajax({
			type: "POST",
			url: feedback_handler,
			data: JSON.stringify(feedback)
		})
		.done(function(data) {
			if(data.success) {
				$('.rating .error', element).hide();
			} else {
				$('.rating .error', element).show();
				$('.rating .error', element).text(data.response);
			}
		});
	});

	if( $(element).find('#your-choice').attr('read-value') < 0) {
		$(element).find('#your-choice').hide();
	} else {
		$(element).find('#your-choice').show();
	}
}
