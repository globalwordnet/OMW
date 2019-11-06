$(function() {
    $("#proj-selector").change(function () {
	var target = '#proj-details';
    $.getJSON($SCRIPT_ROOT + '/_load_proj_details', {
	    proj: $('select[name="proj-selector"]').val()
	}, function(data) {
	    $(target).html(data.result);
	});
	return false;
    });
});


$(function() {
   $("#add-new-project").click(function (event) {

       swal({
	   title: "You can add a new project code below!",
	   input: "text",
	   showCancelButton: true,
	   allowOutsideClick: true,
	   closeOnConfirm: false,
	   animation: "slide-from-top",
	   inputPlaceholder: "New project code",
	   buttonsStyling: false
	   }).then(function(inputValue){
	       if (inputValue === false) return false;
	       if (inputValue === "") {
	    	   swal.showInputError("You need to write something!");
	    	   return false
	       }

           $.getJSON($SCRIPT_ROOT + "/_add_new_project", {
		   user: $('input[name="current_user"]').val(),
		   proj_code: inputValue
	       }, function(data) {

		   if (data.result) {
		       swal("The new project was saved!", "New project: " + inputValue , "success");
		   }
	       });
	   });
       return false;
   });
});


$(function() {
   $("#add_new_language").click(function (event) {

       swal({
	   title: 'Add New Language',
	   showCancelButton: true,
	   confirmButtonText: 'Add Language!',
	   cancelButtonText: 'No, cancel!',
	   buttonsStyling: false,
	   html: "<br><table cellpadding='0' cellspacing='0' border='0'>"+
	         "<tr><td>BCP47:</td><td><input id='bcp47'></input></td>"+
	         "</tr><tr><td>ISO639:</td><td><input id='iso639'></input></td></tr>"+
	         "<tr><td>English Name:</td><td><input id='lang_name'></input></td></tr></table>",

	   preConfirm: function() {
	       return new Promise(function(resolve) {

		   var result = resolve([
		       $('#bcp47').val(),
		       $('#iso639').val(),
		       $('#lang_name').val()
		   ]);

	       });
	   }
       }).then(function(result) {


	   $.getJSON($SCRIPT_ROOT + '/_add_new_language', {
	       user: $('input[name="current_user"]').val(),
	       bcp: result[0],
	       iso: result[1],
	       name: result[2],
	   }, function(data) {

	       if (data.result) {
		   swal("The new language was added!", "New language: " + result , "success");
	       } else {
		   swal("Something went wrong.", "You need to provide at least the BPC47"+
			"code and the English name to add a new language." , "error");

		   }
	   });
       })
       return false;
   });
});






///////////////////////////////////////////////////////////////////////////////
// Bootstrap-based tooltips
///////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('.sense').tooltip({
        title: getSenseTooltip,
        html: true,
        container: 'body'
    });
});


var senseTooltips = Array();

function getSenseTooltip() {
    var element = $(this);

    var id = element[0].attributes['data-sid'].value;

    if(id in senseTooltips){
        return senseTooltips[id];
    }

    var localData = "error";
    $.ajax($SCRIPT_ROOT + '/_load_min_omw_sense/'+id, {
        async: false,
        success: function(data) {
            localData = data.result;
        }
    });

    senseTooltips[id] = localData;

    return localData;
}

$(document).ready(function() {
    $('.synset').tooltip({
        title: getSynsetTooltip,
        html: true,
        container: 'body'
    });
});


var synsetTooltips = Array();
var iliTooltips = Array();

function getSynsetTooltip() {
    var element = $(this);

    var synsetid = element[0].attributes['data-synset'].value;
    var iliid = element[0].attributes['data-iliid'].value;

    if(synsetid) {
        if(synsetid in synsetTooltips){
            return synsetTooltips[id];
        }

        var localData = "error";
        $.ajax($SCRIPT_ROOT + '/_load_min_omw_concept/'+synsetid, {
            async: false,
            success: function(data) {
                localData = data.result;
            }
        });
        synsetTooltips[id] = localData;
    } else {
        if(iliid in iliTooltips){
            return iliTooltips[id];
        }

        var localData = "error";
        $.ajax($SCRIPT_ROOT + '/_load_min_omw_concept_ili/'+ilid, {
            async: false,
            success: function(data) {
                localData = data.result;
            }
        });
        iliTooltips[id] = localData;
    }

    return localData;
}


////////////////////////////////////////////////////////////////////////////////
// These next three functions show the divtooltip with concept details
////////////////////////////////////////////////////////////////////////////////
//$(function() {
//    $(".synset").hover(function (event) {
//
//	var elem = event.target;
//	var synsetid = elem.dataset.synsetid;
//	var iliid = elem.dataset.iliid;
//
//	if (synsetid) {
//	    $.getJSON($SCRIPT_ROOT + '/_load_min_omw_concept/'+synsetid, {
//	    }, function(data) {
//		var divtool = document.getElementById("divtooltip");
//		divtool.innerHTML = data.result;
//	    });
//	} else {
//	    $.getJSON($SCRIPT_ROOT + '/_load_min_omw_concept_ili/'+iliid, {
//	    }, function(data) {
//		var divtool = document.getElementById("divtooltip");
//		divtool.innerHTML = data.result;
//	    });
//	}
//    });
//});
//
//$(function() {
//    $(".synset").mouseenter( function() {
//	$("#divtooltip").show();
//
//	// Get the div-tooltip to move with the mouse
//	$(document).mousemove(function(event){
//	var tooltipSpan = document.getElementById('divtooltip');
//	tooltipSpan.style.top = (event.pageY + 20) + 'px';
//	tooltipSpan.style.left = (event.pageX + 20) + 'px';
//	});
//
//    });
//});
//
//$(function() {
//    $(".synset").mouseleave( function() {
//	$("#divtooltip").hide();
//    });
//});
//////////////////////////////////////////////////////////////////////////////////
//
//
//////////////////////////////////////////////////////////////////////////////////
//// These next three functions show the divtooltip with sense details
//////////////////////////////////////////////////////////////////////////////////
//$(function() {
//    $(".sense").hover(function (event) {
//
//	var elem = event.target;
//	var sid = elem.dataset.sid;
//
//	if (sid) {
//	    $.getJSON($SCRIPT_ROOT + '/_load_min_omw_sense/'+sid, {
//	    }, function(data) {
//		var divtool = document.getElementById("divtooltip");
//		divtool.innerHTML = data.result;
//	    });
//	}
//    });
//});
//
//$(function() {
//    $(".sense").mouseenter( function() {
//	$("#divtooltip").show();
//
//	// Get the div-tooltip to move with the mouse
//	$(document).mousemove(function(event){
//	var tooltipSpan = document.getElementById('divtooltip');
//	tooltipSpan.style.top = (event.pageY + 20) + 'px';
//	tooltipSpan.style.left = (event.pageX + 20) + 'px';
//	});
//
//    });
//});
//
//$(function() {
//    $(".sense").mouseleave( function() {
//	$("#divtooltip").hide();
//    });
//});
//
//// Start with the divtooltip hidden
//$(function() {
//    $("#divtooltip").hide();
//});
//////////////////////////////////////////////////////////////////////////////////
