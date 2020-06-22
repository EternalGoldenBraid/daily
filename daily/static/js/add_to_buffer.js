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
            //globals.response_obj = response
            //globals.dr = response[ev]
            //globals.addRow(globals.table_confirm)

            /* 
             * Reloading the page since the buttons for removing and editing
             * entries in the confirmevents table are rendered with jinja
             * on page load. In future either change the page load for 
             * js only or server side only.
             * All the pre comment code above renders a table asynch.
            location.reload();
             */
        }).fail(function(error) {
        });
    });
  });
