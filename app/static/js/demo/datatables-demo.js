// Call the dataTables jQuery plugin
$(document).ready(function() {
  $('#dataTable').DataTable();
  $("a.mailButton").click(function() {
    $.ajax({
      type: 'POST',
      url: "http://127.0.0.1:5000/send_mail",
      data: {email: $(this).data("email"), name: $(this).data("full_name")}, //passing some input here
      dataType: "text",
      success: function(response) {
          // output.value = response;
          alert(response);
      }
    }).done(function(data){
          console.log(data);
  });
  });

});
