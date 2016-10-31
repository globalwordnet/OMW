$(function() {
    $(document).ready(function(){

	var val2 = document.getElementById("val2");
	val2.innerHTML = "<div style='text-align:center; font-size: 250%;'><i class='fa fa-spinner fa-pulse fa-4x fa-fw'></i></div>";

	var msg = document.getElementById("msg");

	$.getJSON($SCRIPT_ROOT + '/_report_val2', {
	    fn: $('input[name="fn"]').val()
	}, function(data) {

	    if (data.result) {
		r = String(data.result);
		msg.innerHTML = "";
		val2.innerHTML = r;
	    } else {
		val2.innerHTML = "ERROR!!!";
		swal('Oh noes!',
		     'Something bad happened. Please report this!',
		     'error');
	    }

	});




    });
});
