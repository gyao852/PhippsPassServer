// Call the dataTables jQuery plugin
$(document).ready(function () {
    $('#dataTable').DataTable();
    $("a.mailButton").click(function () {
        if ($(this).data("last_sent") === undefined) {
            $.ajax({
                type: 'POST',
                url: "/send_mail",
                data: {email: $(this).data("email"), name: $(this).data("full_name"), authtok: $(this).data("auth")}, //passing some input here
                dataType: "text",
                success: function (data) {
                    $('#successAlert').text("Pass has been sent!").show();
                }
            }).done(function (data) {
                console.log(data);
            });
        } else {
            if (confirm("This member has already been sent an email with their pass on " + $(this).data("last_sent") + ". Are you sure you would like to continue?")) {
                $.ajax({
                    type: 'POST',
                    url: "/send_mail",
                    data: {
                        email: $(this).data("email"),
                        name: $(this).data("full_name"),
                        authtok: $(this).data("auth")
                    }, //passing some input here
                    dataType: "text",
                    success: function (data) {
                        if (data['status'] == 'success') {
                            $('#successAlert').text("Pass has been sent!").show();
                        } else {
                            $('#successAlert').text("An internal error occured. Please retry again or contact server manager.").show();
                        }

                    }
                }).done(function (data) {
                    console.log(data);
                });
            }
        }

    });
});
