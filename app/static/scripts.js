$(document).ready(function() {
    $('input.agree, input.disagree').click(e => {
        e.preventDefault();

        let button = $(e.target);
        let form = button.parents('form');

        form_data = form.serialize();
        button_name = button.attr('name');
        button_value = button.attr('value');

        data = `${form_data}&${button_name}=${button_value}`;

        $.ajax({
            type: 'POST',
            url: form.attr('action'),
            data: data,
            success: data => {
                Object.entries(data['votes']).map(([key, value], _) => {
                    console.log(key);
                    console.log(value);
                    console.log(`input#${key}-${data['rid']}`)
                    let btn = $(`input#${key}-${data['rid']}`);
                    console.log(btn);
                    btn.attr('value', value)
                });
                // console.log(data[button_name]);
                // console.log(`${button_value.split(' ')[0]} ${data[button_name]}`)
                // let btn = $(`input#${button_name}-${data['rid']}`)
                // btn.text(`${button_value.split(' ')[0]} ${data[button_name]}`)
            },

            beforeSend: (xhr, settings) => {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", form.find('input[name=csrf_token]').val())
                }
            }
        });
    });
});

