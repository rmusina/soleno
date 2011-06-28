$(document).ready(function(){
    $("#lecture_session_slider_trigger").click(function(){
        $("#lecture_session_slider").toggle("fast");
        $(this).toggleClass("active");
    	scrollToBottom($("#session_updates_container"));
        return false;
    });
    	
	$.cleditor.buttons.save.buttonClick = function(e, data){
		var html_text = data.editor.$area[0].value;
		postEditorData(html_text);
		
		return true;
	};
	
	function postEditorData(editorData) {
		$.post("./new", { 
			data: editorData
		}, function(data) {
			var currentTime = new Date();
			$("#note_status").text(data + " " + currentTime.getHours() + ":" + currentTime.getMinutes());
			
			var html_text = editorData;
			var plain_text = html_text.replace(/(<([^>]+)>)/ig,"");
			updateKeywords(plain_text, html_text);
			
		});
	}

	updater.poll();
});

$(function() {	
	function initializeDraggableDropableCanvas() {
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
	}
	
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
	
	function convertNameToIdReference(elementIdName) {
		return "#" + elementIdName;
	}
		
	function createNoteWindow(updateId, 
							  updateAuthor, 
							  updateTime,
							  positionLeft,
							  positionTop, 
							  ui) {
		
		var notesContainerId = "notes_container_" + updateId;
		var noteTextId = "note_text_" + updateId;
		
		var notes_container_div = "<div id=\"" + notesContainerId +  "\" class=\"notes_container\"> " +
								  		"<div class=\"notes_container_header\">" +
								  			"<div class=\"notes_container_title\">" + updateAuthor + "'s notes saved at " + updateTime + "</div>" +
								  			"<a class=\"notes_container_close_btn\" href=\"#\">x</a>" +
								  			"<div class=\"notes_container_clearer\"/>" +
								  		"</div>" +
									  	"<div class=\"textarea_div\">" +
									  		"<textarea id=\"" + noteTextId + "\" class=\"note_text\"></textarea>" +
										"</div>" +
								  "</div>";
		
		$("#lecture_session_container").append(notes_container_div).show("slow");
		
		var notesContainerIdReference = convertNameToIdReference(notesContainerId);
		var notesTextIdReference = convertNameToIdReference(noteTextId);
				
		addControlsToNotesContainer(notesContainerIdReference, notesTextIdReference, positionLeft, positionTop, false);
		
		$(notesContainerIdReference + " .notes_container_header a").bind("click", function(){
			$('div').remove(notesContainerIdReference);
			ui.draggable.show('slow');
		});
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
	
	function addToolboxAccordionContainer() {
		$("#toolbox_container").draggable({
			handle: ".notes_container_header",
			containment:"#lecture_session_container",
			scroll: false,
			iframeFix: true,
			stack: "#lecture_session_container div"
		}).resizable({
			minWidth: 300,
			minHeight: 400,
			containment:"#lecture_session_container",
			scroll: false,
			resize: function(event, ui) {
				$( "#toolbox_accordion" ).accordion( "resize" );
			}
		}).position({
		    "my": "right top",
		    "at": "right top",
		    "offset": "0 30",
		    "of": $("#lecture_session_container")
		});;
		
		$("#toolbox_accordion").accordion({
			fillSpace: true
		});
	}
	
	function getKeyTerms(text) {
		
	}
	
	function getRepetitions(text) {
		var sentences = text.split();
	}
	
	addControlsToNotesContainer(".notes_container", ".note_text");
	
	addToolboxAccordionContainer();
	
	initializeDraggableDropableCanvas();
});


/* comet connection related stuff */

function addUpdateToSidebar(update) {
	
	var update_li = "<li class=\"session_update ui-draggable\">" + 
						"<input type=\"hidden\" name=\"session_update_id\" value=\"" + update.id + "\"/>" + 
						update.created_by_avatar_src +
						"<div class=\"user_data\">" +
							"<p><a href=\".\">" + update.created_by_username + "</a></p>" +
							"<p>4.6/5</p> " +
						"</div>" + 
						"<div class=\"update_time\">" + 
							"<p>" + update.saved_at + "</p>" +
						"</div>" + 
					"</li>";
	
	$("#session_updates_container").append(update_li).show('slow');
	
	scrollToBottom($("#session_updates_container"));	
} 

function scrollToBottom(container) {
	container.animate({
		scrollTop: container[0].scrollHeight - container.height()
	});
}

var updater = {
	errorSleepTime: 500,
	
	clientId: -1,

	poll: function() {
        $.ajax({url: "./updates", 
        		type: "POST", 
        		dataType: "text",
                data: {
                	clientId: -1,
                }, 
                success: updater.onSuccess,
                error: updater.onError});
    },

    onSuccess: function(response) {
    	try {
            updater.newUpdates(eval("(" + response + ")"));
        } catch (e) {
            updater.onError();
            return;
        }
        updater.errorSleepTime = 500;
        window.setTimeout(updater.poll, 0);
    },

    onError: function(response) {
        updater.errorSleepTime *= 2;
        console.log("Poll error; sleeping for", updater.errorSleepTime, "ms");
        window.setTimeout(updater.poll, updater.errorSleepTime);
    },

    newUpdates: function(response) {
    	if (!response.updates) return;
    	
        var updates = response.updates;
        
        updater.lastMessageId = updates[updates.length - 1].id;
        
        for (var i = 0; i < updates.length; i++) {
            updater.showUpdate(updates[i]);
        }
    },

    showUpdate: function(update) {
    	/*var existing = $("#session_update input").find("input[type=hidden]").val(update.id).select(); // not sure if working
        if (existing.length > 0) return;*/
        
        //add to sidebar
        addUpdateToSidebar(update);
    }    
}

/* keyword finding stuff */

this.imagePreview = function(){	
	xOffset = 10;
	yOffset = 30;

	$("#nopsa_images img").hover(function(e){
		this.t = this.title;
		this.title = "";	
		var c = (this.t != "") ? "<br/>" + this.t : "";
		$("#body").append("<p id='preview'><img src='"+ this.src +"' alt='Image preview' />"+ c +"</p>");								 
		$("#preview")
			.css("top",(e.pageY - xOffset) + "px")
			.css("left",(e.pageX + yOffset) + "px")
			.fadeIn("fast");						
    },
	function(){
		this.title = this.t;	
		$("#preview").remove();
    });	
	
	$("#nopsa_images img").mousemove(function(e){
		$("#preview")
			.css("top",(e.pageY - xOffset) + "px")
			.css("left",(e.pageX + yOffset) + "px");
	});
	
	$("#nopsa_images img").mousedown(function () {
		this.title = this.t;	
		$("#preview").remove();
	});
};

function updateKeywords(plain_text, html_text) {
	var keyterms = getKeyTerms(plain_text, html_text);
	
	$.post("./keywords", {
			occurrences: JSON.stringify(keyterms.value),
			parts_of_speech: JSON.stringify(keyterms.POS),
			is_highlighted: JSON.stringify(keyterms.isHighlighted)
		}, 
		function(response) {
			$("#keyterms_container").html("");
			$("#nopsa_images").html("");
			
			var responseJSON = JSON.parse(response);
			
			for (var key in responseJSON["similarity_ratings"]) {
				if (responseJSON["similarity_ratings"].hasOwnProperty(key)) {
					$("#keyterms_container").append("<li>" + responseJSON["similarity_ratings"][key][0] + 
							"  <b>" + responseJSON["similarity_ratings"][key][1]  + "</b></li>");
				}
		    }
			
			for (var i = 0; i < responseJSON["fetched_images"].length; i++) {
				$("#nopsa_images").append(responseJSON["fetched_images"][i]);
		    }
			
			imagePreview();
		})
		.error(function(response) {
			alert("The server was unable to process your request. It might be malformed");
		});
}
