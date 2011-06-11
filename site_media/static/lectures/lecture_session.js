$(document).ready(function(){
    $("#lecture_session_slider_trigger").click(function(){
        $("#lecture_session_slider").toggle("fast");
        $(this).toggleClass("active");
        return false;
    });

    $("#note_text").cleditor({
    	width:     "100%",
    	height:    "260px",
    	bodyStyle: "margin:4px; font:10pt Arial,Verdana; cursor:text"
    });
});

$(function() {
	$( ".notes_container" ).draggable({
		handle:".notes_container_header",
		containment:"#lecture_session_container",
		scroll: false
	}).resizable({
		minWidth: 400,
		minHeight: 300,
		containment:"#lecture_session_container",
		scroll: false,
		resize: function(event, ui) {
			$("#note_text").cleditor()[0].$main.height($(event.target).height()-40); //-40 compensates for header
		}
	}).position({
	    "my": "left top",
	    "at": "left top",
	    "offset": "200 30",
	    "of": $("#lecture_session_container")
	});
});

