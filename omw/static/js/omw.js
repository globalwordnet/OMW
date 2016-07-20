
$( document ).ready(function() {
    $.getJSON($SCRIPT_ROOT + '/_load_lang_selector', {
    }, function(data) {
	var langsel = document.getElementById("LangSelector");
	langsel.innerHTML = data.result;
    });
});
