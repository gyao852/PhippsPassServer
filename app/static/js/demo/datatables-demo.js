// Call the dataTables jQuery plugin
$(document).ready(function() {
  $('#dataTable').DataTable();
  $("a.mailButton").click(function() {
    $.ajax({
      type: 'POST',
      url: "/send_mail",
      data: {email: $(this).data("email"), name: $(this).data("full_name"), authtok: $(this).data("auth") }, //passing some input here
      dataType: "text",
      success: function(response) {
          alert("Pass sent. Remove this alert in the future.");
      }
    }).done(function(data){
          console.log(data);
  });
  });

});
