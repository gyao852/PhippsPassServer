// Call the dataTables jQuery plugin
$(document).ready(function () {
    $('#dataTable').DataTable();
    $("a.mailButton, #send-multiple-passes").click(function () {
        var selected = [];
        $("input[name='send_mail']:checked").each(function () {
            var aRow = {
                "name": $(this).closest('tr')[0].cells[2].innerText,
                "email": $(this).closest('tr')[0].cells[8].children[0].getAttribute("data-email"),
                "auth": $(this).closest('tr')[0].cells[8].children[0].getAttribute("data-auth")
            };
            selected.push(aRow);
        });
        if ($(this).data("last_sent") === undefined) {
            $.ajax({
                type: 'POST',
                url: "/send_mail",
                data: {
                    selected: JSON.stringify(selected),
                    email: $(this).data("email"),
                    name: $(this).data("full_name"),
                    authtok: $(this).data("auth")
                }}).done(function (data) {
                if (data['count'] === 0) {
                    $('#errorAlert').text("An internal error occurred. Please retry again or contact server manager.").show();
                    $('#successAlert').hide();

                } else {
                    $('#successAlert').text(data['count'] + " passes have been sent!").show();
                    $('#errorAlert').hide();
                }
            });
        } else {
            if (confirm("This member has already been sent an email with their pass on " + $(this).data("last_sent") + ". Are you sure you would like to continue?")) {
                $.ajax({
                    type: 'POST',
                    url: "/send_mail",
                    data: {
                        selected: JSON.stringify(selected),
                        email: $(this).data("email"),
                        name: $(this).data("full_name"),
                        authtok: $(this).data("auth")
                    }}).done(function (data) {
                    if (data['count'] === 0) {
                        $('#errorAlert').text("An internal error occurred. Please retry again or contact server manager.").show();
                        $('#successAlert').hide();
                    } else {
                        $('#successAlert').text(data['count'] + " pass has been sent!").show();
                        $('#errorAlert').hide();
                    }
                });
            }
        }

    });
});
