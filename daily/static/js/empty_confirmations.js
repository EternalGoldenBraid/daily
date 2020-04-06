$(function() {
    $('#eventclear').on('click', function(event) {
        event.preventDefault();

        $.post($SCRIPT_ROOT + '/empty', {

        }).done(function(response) {
            let table = document.querySelector("#confirmevents")
            $("#confirmevents").hide();
            console.log("Emptied response: ", response)
        }).fail(function() {
            // Debug
            console.log("Failed to empty")
        });
    });
  });

