function RatingXBlock(runtime, element) {
  $(element).find('.save-button').bind('click', function() {
    var handlerUrl = runtime.handlerUrl(element, 'studio_submit');
    var data = {
      rating: $(element).find('input[name=rating]').val(),
      text: $(element).find('input[name=text]').val(),
      title: $(element).find('input[name=title]').val(),
      thankyou: $(element).find('input[name=thankyou]').val(),
      error: $(element).find('input[name=error]').val()
    };
    runtime.notify('save', {state: 'start'});
    $.post(handlerUrl, JSON.stringify(data)).done(function(response) {
      runtime.notify('save', {state: 'end'});
    });
  });

  $(element).find('.cancel-button').bind('click', function() {
    runtime.notify('cancel', {});
  });
}
