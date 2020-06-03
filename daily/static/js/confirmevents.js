  $(function() {
    $('#eventsubmit').on('click', function(event) {
        event.preventDefault();
	let ev = $('#event_field').val();
	let dr_h = $('input[name="duration_event_hours"]').val();
	let dr_m = $('input[name="duration_event_minutes"]').val();

        globals.ev = ev;

        $.post($SCRIPT_ROOT + '/events_confirm', {
	    event: globals.ev,
	    duration_hours: dr_h,
	    duration_minutes: dr_m,
        }).done(function(response) {
            // Add table row
            globals.response_obj = response
            globals.dr = response[ev]
            globals.addRow(globals.table_confirm)
            // test
            console.log("globals.response: ", globals.response_obj)
        }).fail(function(error) {
            console.log(error.responseText)
            console.log("confirmevents failed to add event")
        });
    });
  });
