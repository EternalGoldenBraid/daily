$(function() {
    $('#eventclear').on('click', function(event) {
        event.preventDefault();

        $.post($SCRIPT_ROOT + '/empty', {

        }).done(function(response) {
            //Jqueyr altenative
            //tbl = $("#confirmevents");
            
            // find table 'confirmevents'
            let tbl = document.getElementsByTagName('table')[1];
            tbl.remove();
        }).fail(function() {
            console.log("Failed to empty")
        });
    });
  });

