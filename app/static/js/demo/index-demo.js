// Call the dataTables jQuery plugin
$(document).ready(function () {
        $("#reset-database-btn").click(function (event) {
        $.ajax({
            type: 'POST',
            url: "reset_database",
            data: {}, //passing some input here
            processData: false,
            contentType: false
        }).done(function (data) {
            if (data['count'] === 0) {
                $('#errorAlert').text("Database could not be reset. Please contact server manager.").show();
                $('#successAlert').hide();
            } else {
                $('#successAlert').text("Database was reset. All values have been cleared.").show();
                $('#errorAlert').hide();
            }
        });
        event.preventDefault();

    });

});
