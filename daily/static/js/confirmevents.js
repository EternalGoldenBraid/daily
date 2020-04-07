  $(function() {
    $('#eventsubmits').on('click', function(event) {
        event.preventDefault();
	let ev = $('input[name="event"]').val();
	let dr = $('input[name="duration_event"]').val();
        let description={"event": globals.ev, "duration": dr};

        globals.ev = ev;
        globals.dr = dr;

        $.post($SCRIPT_ROOT + '/events_confirm', {
	    event: globals.ev,
	    duration: globals.dr 
        }).done(function(response) {
            // Add table row
            globals.response_obj = response
            globals.addRow(globals.table_confirm)
        }).fail(function(error) {
            // Debug
            alert(error.responseText);
        });
    });
  });
