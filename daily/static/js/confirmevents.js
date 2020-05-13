  $(function() {
    $('#eventsubmits').on('click', function(event) {
        event.preventDefault();
	let ev = $('input[name="event"]').val();
	let dr_h = $('input[name="duration_event_hours"]').val();
	let dr_m = $('input[name="duration_event_minutes"]').val();
        //let description={"event": globals.ev, "duration": dr};

        // Convert duration to minutes
        let dr = null
        if (dr_h !== null || dr_m !== null) {
            if (dr_h === null) {
                dr = dr_m 
            } else if (dr_m === null) {
                dr = dr_h*60
            } else {
                dr = dr_h*60 + dr_m} 
        }
        globals.ev = ev;
        globals.dr = dr;

        $.post($SCRIPT_ROOT + '/events_confirm', {
	    event: globals.ev,
	    duration: globals.dr,
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
