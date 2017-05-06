function validate_email(field,alerttxt) {
	with (field) {
		apos = value.indexOf("@");
		dotpos = value.lastIndexOf(".");
		if (apos<1||dotpos-apos<2) {
			alert(alerttxt);
			return false;
		} else {
			return true;
		}
	}
}
function topassword() {
    //document.write("Hello World!");
    var p1 = document.getElementById("password1").value;
    var p2 = document.getElementById("password2").value;
    if (p1 == p2) {
        //alert("password right");
        return true;
    } else {
        alert("password wrong");
        return false;
    }
}
function validate_form(thisform) {
	with (thisform) {
		if (validate_email(email,"Not a valid e-mail address!")==false) {
			email.focus();
			return false;
		}
		return topassword();
	}
}


$('#loginform').submit(function(e) {
    var form = $(this);
    var formdata = false;
    if(window.FormData) {
        formdata = new FormData(form[0]);
    }
    var formAction = form.attr('action');
    $.ajax({
        type    :   'POST',
        url     :   '/login',
        cache   :   false,
        data    :   formdata ? formdata : form.serialize(),
        contentType:false,
        processData:false,
        dataType:'json',
        success:function(response) {
            if (response.result == true) {
                $('#loginmessage').addClass('alert alert-success').text(response.message);
                location.href = response.next;
            } else {
                $('#loginmessage').addClass('alert alert-danger').text(response.message);
            }
        }
    });
    e.preventDefault();
});


$('#mylogin').on('hidden.bs.modal', function () {
    $(this).find('form').trigger('reset');
    $('#loginmessage').removeClass('alert alert-danger').text('');
})