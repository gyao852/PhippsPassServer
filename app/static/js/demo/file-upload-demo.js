// Call the dataTables jQuery plugin
$(document).ready(function () {
        $("#upload-file-btn").click(function (event) {
        var form_data = new FormData($('#upload-file')[0]);
        $.ajax({
            type: 'POST',
            url: "upload_membership",
            data: form_data, //passing some input here
            processData: false,
            contentType: false
        }).done(function (data) {
            if (data['count'] === 0) {
                $('#errorAlert').text("An error occurred when uploading the new membership data. Please ensure that " +
                    "the schema matches, and all number-like fields are set as 'Text'.").show();
                $('#successAlert').hide();
            } else {
                $('#successAlert').text(data['count'] + " records have been created or updated!").show();
                $('#errorAlert').hide();
            }
        });
        event.preventDefault();

    });

});
