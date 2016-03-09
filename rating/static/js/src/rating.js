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
		var rating = 0;
		if ($(".rating_radio:checked", element).length === 0) {
			rating = -1;
		} else {
			rating = parseInt($(".rating_radio:checked", element).attr("id").split("_")[1]);
		}
		var feedback = {"text": text, 
		"rating": rating};
		Logger.log("edx.ratingxblock.submit", feedback);
		$.ajax({
			type: "POST",
			url: feedback_handler,
			data: JSON.stringify(feedback),
			success: function(data) {$('.rating .thankyou', element).text(data.response);}
		});
	});

	/**

	$('.rating_radio', element).change(function(eventObject) {
		var target_id = eventObject.target.id;
		var rating = parseInt(target_id.split('_')[1]);
		Logger.log("edx.ratingxblock.rating", {"rating":rating});
	});

	$('.rating_text_area', element).change(function(eventObject) {
		var text = eventObject.currentTarget.value;
		Logger.log("edx.ratingxblock.text", {"text":text});
	});
    **/
}
