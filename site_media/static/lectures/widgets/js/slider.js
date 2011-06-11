$(function() {
	$( "#slider-range-min" ).slider({
		range: "min",
		animate: false,
		value: 45,
		min: 45,
		max: 240,
		slide: function( event, ui ) {
			updateValues(event, ui);
		},
		change: function(event, ui) {
			updateValues(event, ui);
	    }
	});
	
	function updateValues(event, ui)
    {
		$( "#id_lecture_duration" ).val( ui.value );
		$('#current_value').text( $( "#slider-range-min" ).slider( "value" ) + " minutes");
    }
	
	$( "#id_lecture_duration" ).val( $( "#slider-range-min" ).slider( "value" ) );
	$('#current_value').text( $( "#slider-range-min" ).slider( "value" ) + " minutes");
});