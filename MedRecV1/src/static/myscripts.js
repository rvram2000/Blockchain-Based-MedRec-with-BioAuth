
$().ready(function() {


    $("#frm").validate({
    rules: {
    
          registerNo: "required",
          doctorName: "required",
          
        },

    messages: {
          registerNo: "Invalid Register No",
          doctorName: "Invalid Doctor Name"
        },
    submitHandler: function(form) {
          form.submit();
        }
    });
});