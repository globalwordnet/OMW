
$(function() {
    $(".thumbup").click(function (event) {

	var elem = event.target;
	var elem = elem.parentNode;
	var ili = elem.dataset.ili;
	var target = '#rating'+String(ili);
	var tup = '#thumbup'+String(ili);
	var tdown = '#thumbdown'+String(ili);

	$.getJSON($SCRIPT_ROOT + '/_thumb_up_id', {
	    user: $('input[name="current_user"]').val(),
	    ili_id: ili
	}, function(data) {
	    $(target).html(data.result);
	    $(tdown).html('<i class="fa fa-thumbs-o-down" aria-hidden="true"></i>');
	    $(tup).html('<i class="fa fa-thumbs-o-down" aria-hidden="true"></i>');
	    $(tup).html('<i class="fa fa-thumbs-o-up" aria-hidden="true" style="color:green"></i>');
	});
	return false;
    });
});


$(function() {
    $(".thumbdown").click(function (event) {

	var elem = event.target;
	var elem = elem.parentNode;
	var ili = elem.dataset.ili;
	var target = '#rating'+String(ili);
	var tup = '#thumbup'+String(ili);
	var tdown = '#thumbdown'+String(ili);

	$.getJSON($SCRIPT_ROOT + '/_thumb_down_id', {
	    user: $('input[name="current_user"]').val(),
	    ili_id: ili
	}, function(data) {
	    $(target).html(data.result);
	    $(tdown).html('<i class="fa fa-thumbs-o-down" aria-hidden="true"></i>');
	    $(tup).html('<i class="fa fa-thumbs-o-up" aria-hidden="true"></i>');
	    $(tdown).html('<i class="fa fa-thumbs-o-down" aria-hidden="true" style="color:red"></i>');
	});
	return false;
    });
});


$(function() {
    $(".detailed").click(function (event) {

	var elem = event.target;
	var elem = elem.parentNode;
	var ili = elem.dataset.ili;
	var target = '#seedetailed'+String(ili);
	var det = '#detailed'+String(ili);

	$.getJSON($SCRIPT_ROOT + '/_detailed_id', {
	    ili_id: ili
	}, function(data) {
	    $(target).html(data.result);

	    if ($(det).html() == '<i class="fa fa-toggle-off" aria-hidden="true"></i>'){
		$(det).html('<i class="fa fa-toggle-on" aria-hidden="true"></i>');
		$(target).html(data.result);
	    } else {
		$(det).html('<i class="fa fa-toggle-off" aria-hidden="true"></i>');
		$(target).html('');
	    }
	});
	return false;
    });
});



// $(function() {
//     $("#confirm_wn_upload").click(function(event) {

// 	swal({
// 	    title: 'Are you sure?',
// 	    text: "The upload of this wordnet cannot be reverted! Please wait after confirming. It may take a while to refresh the page.",
// 	    type: 'warning',
// 	    showCancelButton: true,
// 	    confirmButtonText: 'Yes, upload it!',
// 	    cancelButtonText: 'No, cancel!',
// 	    showLoaderOnConfirm: true,
// 	    buttonsStyling: false
// 	}).then(function() {

// 	    var valid = document.getElementById("validation_div");
// 	    valid.innerHTML = "<i class='fa fa-spinner fa-pulse fa-5x fa-fw'></i><span class='sr-only'><br><br> This process can take a little while (depending how big is the uploaded wordnet)... Just hang in there.</span>";

// 	    $.getJSON($SCRIPT_ROOT + '/_confirm_wn_upload', {
// 		user: $('input[name="current_user"]').val(),
// 		fn: $('input[name="fn"]').val(),

// 	    }, function(data) {

// 		var u = $('input[name="current_user"]').val();

// 		if (data.result) {
// 		    r = String(data.result);
// 		    window.location.replace($SCRIPT_ROOT + "/temporary");

// 		} else {
// 		    swal('Oh noes!',
// 			'Something bad happened. Please report this!',
// 			'error');
// 		}
// 	    });

// 	}, function(dismiss) {
// 	    if (dismiss === 'cancel') {
// 		swal(
// 		    'Cancelled',
// 		    'No changes were made to ILI :)',
// 		    'error'
// 		);
// 	    }
// 	})
//     });
// });


// function change() {
//   var val = document.getElementById("confirm_wn_upload");
//   val.innerHTML = "<div style='text-align:center; font-size: 250%;'><i class='fa fa-spinner fa-pulse fa-4x fa-fw'></i></div>";
// };


$(function() {
   $(".comment").click(function (event) {

       var elem = event.target;
       var elem = elem.parentNode;
       var ili = elem.dataset.ili;

       swal({
	   title: "Leave your comment below!",
	   input: "textarea",
	   showCancelButton: true,
	   allowOutsideClick: true,
	   closeOnConfirm: false,
	   animation: "slide-from-top",
	   inputPlaceholder: "Your comment goes here",
	   buttonsStyling: false
	   }).then(function(inputValue){
	       if (inputValue === false) return false;
	       if (inputValue === "") {
	    	   swal.showInputError("You need to write something!");
	    	   return false
	       }

	       $.getJSON($SCRIPT_ROOT + '/_comment_id', {
		   user: $('input[name="current_user"]').val(),
		   ili_id: ili,
		   comment: inputValue
	       }, function(data) {

		   if (data.result) {
		       swal("The comment was saved!", "" , "success");
		   }

	       });
	   });
       return false;
   });
});

