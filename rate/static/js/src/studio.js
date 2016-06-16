function RatingXBlock(runtime, element) {
    $(element).find('.save-button').bind('click', function () {
        var handlerUrl = runtime.handlerUrl(element, 'studio_submit'),
            data = {
                rating: $(element).find('input[name=rating]').val(),
                text: $(element).find('input[name=text]').val(),
                title: $(element).find('input[name=title]').val(),
                error: $(element).find('input[name=error]').val(),
                show_textarea: $(element).find('select[name=show_textarea]').val()
            };
        runtime.notify('save', {
            state: 'start'
        });
        $.post(handlerUrl, JSON.stringify(data))
        .done(function (response) {
            runtime.notify('save', {
                state: 'end'
            });
        });
    });

    $(element).find('.cancel-button').bind('click', function() {
        runtime.notify('cancel', {});
    });
    var show_textarea = $(element).find('select#show_textarea').attr('default-value');
    console.log(show_textarea);
    $(element).find('select#show_textarea').val(show_textarea);
    if(show_textarea < 1) {
        $(element).find('li.hide-toggle').hide();
    }

    $(element).find('#show_textarea').bind('change', function(event) {
        if($(this).val() == 0) {
            $(element).find('li.hide-toggle').hide();
        } else if ($(this).val() == 1) {
            $(element).find('li.hide-toggle').show();
        }
    });
}