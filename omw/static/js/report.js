$(function() {
    $(document).ready(function(){

	var val1 = document.getElementById("val1");
	val1.innerHTML = "<i class='fa fa-spinner fa-pulse fa-4x fa-fw'></i>";

	var val2 = document.getElementById("val2");
	val2.innerHTML = "<i class='fa fa-spinner fa-pulse fa-4x fa-fw'></i>";	


	$.getJSON($SCRIPT_ROOT + '/_report_val1', {
	    fn: $('input[name="fn"]').val()
	}, function(data) {
	    
	    if (data.result) {
		r = String(data.result);
		val1.innerHTML = r;
		
	    } else {
		val1.innerHTML = "ERROR!!!";
		swal('Oh noes!',
		     'Something bad happened. Please report this!',
		     'error');
	    }
	});


	$.getJSON($SCRIPT_ROOT + '/_report_val2', {
	    fn: $('input[name="fn"]').val()
	}, function(data) {

	    if (data.result) {
		r = String(data.result);
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

// $(function() {
//     $(document).ready(function(){

// 	var val2 = document.getElementById("val2");
// 	val2.innerHTML = "<i class='fa fa-spinner fa-pulse fa-4x fa-fw'></i>";	

// 	$.getJSON($SCRIPT_ROOT + '/_report_val2', {
// 	    fn: $('input[name="fn"]').val()
// 	}, function(data) {

// 	    if (data.result) {
// 		alert(data.result);
// 		r = String(data.result);
// 		val2.innerHTML = r;		
// 	    } else {
// 		val2.innerHTML = "ERROR!!!";
// 		swal('Oh noes!',
// 		     'Something bad happened. Please report this!',
// 		     'error');
// 	    }

// 	});

//     });
// });





$(function() {
    $("#confirm_wn_upload").click(function() {

	swal({
	    title: 'Are you sure?',
	    text: "The upload of this wordnet cannot be reverted! Please wait after confirming. It may take a while to refresh the page.",
	    type: 'warning',
	    showCancelButton: true,
	    confirmButtonText: 'Yes, upload it!',
	    cancelButtonText: 'No, cancel!',
	    showLoaderOnConfirm: true,
	    buttonsStyling: false
	}).then(function() {

	    var valid = document.getElementById("validation_div");
	    valid.innerHTML = "<i class='fa fa-spinner fa-pulse fa-5x fa-fw'></i><span class='sr-only'><br><br> This process can take a little while (depending how big is the uploaded wordnet)... Just hang in there.</span>";

	    $.getJSON($SCRIPT_ROOT + '/_confirm_wn_upload', {
		user: $('input[name="current_user"]').val(),
		fn: $('input[name="fn"]').val(),

	    }, function(data) {

		var u = $('input[name="current_user"]').val();

		if (data.result) {
		    r = String(data.result);
		    window.location.replace($SCRIPT_ROOT + "/temporary");

		} else {
		    swal('Oh noes!',
			'Something bad happened. Please report this!',
			'error');
		}
	    });

	}, function(dismiss) {
	    if (dismiss === 'cancel') {
		swal(
		    'Cancelled',
		    'No changes were made to ILI :)',
		    'error'
		);
	    }
	})
    });
});
