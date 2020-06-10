// hospital search
const user_input = $("#hospitals-search")
const search_icon = $('#h-search-icon')
const hospitals = $('#h-replaceable-content')
const endpoint = '/hospitals/'
const delay_by_in_ms = 1000
let scheduled_function = false

let ajax_call = function (endpoint, request_parameters) {
    $.getJSON(endpoint, request_parameters)
        .done(response => {
            hospitals.fadeTo('300', 0).promise().then(() => {
                hospitals.html(response['html_from_view'])
                hospitals.fadeTo('150', 1)
                search_icon.removeClass('text-white')
            })
        })
}


user_input.on('keyup', function () {

    const request_parameters = {
        q: $(this).val() 
    }

    search_icon.addClass('text-white')

    if (scheduled_function) {
        clearTimeout(scheduled_function)
    }

    scheduled_function = setTimeout(ajax_call, delay_by_in_ms, endpoint, request_parameters)
})