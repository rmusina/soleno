$(document).ready(function(){
    $("#lecture_session_slider_trigger").click(function(){
        $("#lecture_session_slider").toggle("fast");
        $(this).toggleClass("active");
        return false;
    });
    	
	$.cleditor.buttons.save.buttonClick = function(e, data){
		postEditorData(data.editor.$area[0].value);
		return false;
	};
	
	function postEditorData(editorData) {
		$.post(".", { data: editorData }, function(data) {
			alert(data);
		});
	}
});

$(function() {
	
	addControlsToNotesContainer(".notes_container", ".note_text");
	
	$( ".session_update" ).draggable({
		helper: "clone",
		zIndex: 101,
		scroll: false
	});
	
	$("#session_updates_container").sortable({
				
	});
	
	$("#lecture_session_container").droppable({
		greedy: true,
		activeClass: "hover_active ",
		accept: ".session_update",
		drop: function( event, ui ) {
			generateWindowAndPopulateTextArea(event, ui);
			ui.draggable.hide('slow');
		}
	});
	
	function generateWindowAndPopulateTextArea(event, ui) {
		var updateId = $(ui.draggable).children("input").val();
		var updateAuthor = $(ui.draggable).children(".user_data").children("p")[0].children[0].text;
		var updateTime = $(ui.draggable).children(".update_time").children("p")[0].textContent;
		
		createNoteWindow(updateId, updateAuthor, updateTime, ui.position.left, ui.position.top, ui);

		var noteTextId = "#note_text_" + updateId;
		
		getNoteText(updateId, noteTextId);
	}
	
	function getNoteText(updateId, noteTextId) {
		$.get(".", { id: updateId }, function(data){
			var editor = $(noteTextId).cleditor()[0];
			editor.$area.val(data);
			editor.updateFrame();
		});
	}
	
	function createNoteWindow(updateId, 
							  updateAuthor, 
							  updateTime,
							  positionLeft,
							  positionTop, 
							  ui) {
		
		var notes_container_id = "notes_container_" + updateId;
		
		var notes_container_div = "<div id=\"" + notes_container_id +  "\" class=\"notes_container\"> " +
								  		"<div class=\"notes_container_header\">" +
								  			"<div class=\"notes_container_title\">" + updateAuthor + "'s notes saved at " + updateTime + "</div>" +
								  			"<a class=\"notes_container_close_btn\" href=\"#\">x</a>" +
								  			"<div class=\"notes_container_clearer\"/>" +
								  		"</div>" +
									  	"<div class=\"textarea_div\">" +
									  		"<textarea id=\"note_text_" + updateId + "\" class=\"note_text\"></textarea>" +
										"</div>" +
								  "</div>";
		
		$("#lecture_session_container").append(notes_container_div).show("slow");
		
		$("#" + notes_container_id + " .notes_container_header a").bind("click", function(){
			$("#" + notes_container_id).remove();
			ui.draggable.show('slow');
		});
		
		addControlsToNotesContainer("#notes_container_" + updateId,  "#note_text_" + updateId, positionLeft, positionTop, false);
	}
	
	function addControlsToNotesContainer(noteContainerId, 
										 noteTextId,
										 initialOffsetLeft,
										 initialOffsetTop,
										 allowSave) {
		
		if ( initialOffsetLeft === undefined ) {
			initialOffsetLeft = 200;
		}
		
		if ( initialOffsetTop === undefined ) {
			initialOffsetTop = 30;
		}
		
		if ( allowSave === undefined ) {
			allowSave = true;
		}
		
		$( noteContainerId ).draggable({
			handle: ".notes_container_header",
			containment:"#lecture_session_container",
			scroll: false,
			iframeFix: true,
			stack: "#lecture_session_container div"
		}).resizable({
			minWidth: 400,
			minHeight: 300,
			containment:"#lecture_session_container",
			scroll: false,
			resize: function(event, ui) {
				$( noteTextId ).cleditor()[0].$main.height($(event.target).height()-40); //-40 compensates for header
			},			
			/* 
			 * The following are fixes for the iFrame resize problem, as specified here 
			 * http://stackoverflow.com/questions/509118/trouble-using-jquery-ui-resizable-and-ui-draggable-with-an-iframe 
			 */
			start: function(event, ui) {
		        //add a mask over the Iframe to prevent it from stealing mouse events
		        $("#lecture_session_container").append("<div id=\"mask\" style=\"background-image:url(../images/transparent.gif); position: absolute; z-index: 900; left: 0pt; top: 0pt; right: 0pt; bottom: 0pt;\"></div>");
		    },
		    stop: function(event, ui) {
		        //remove mask when dragging ends
		        $("#mask").remove();
		    }
		}).position({
		    "my": "left top",
		    "at": "left top",
		    "offset": String(initialOffsetLeft) + " " + String(initialOffsetTop),
		    "of": $("#lecture_session_container")
		});
		
		$( noteTextId ).cleditor({
	    	width:     "100%",
	    	height:    "100%",
	    	bodyStyle: "margin:4px; font:10pt Arial,Verdana; cursor:text",
	    	controls:
	    	"bold italic underline strikethrough subscript superscript | font size " +
	    	"style | color highlight removeformat | bullets numbering | outdent " +
	    	"indent | alignleft center alignright justify | undo redo | " +
	    	"rule table image link unlink | cut copy paste pastetext | print source " + 
	    	(allowSave ? "| save" : "")
	    });
	}
});



