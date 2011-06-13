(function($) {

	  // Define the table button
	  $.cleditor.buttons.save = {
	    name: "save",
	    image: "save.png",
	    title: "Save",
	    buttonClick: saveButtonClick
	  };
	
	  $.cleditor.defaultOptions.controls = $.cleditor.defaultOptions.controls.replace("rule ", "rule save ");
	
	  function saveButtonClick(e, data) {
		  alert("clicked save");
	  }
})(jQuery);