$(function() {
    $('#eventclear').on('click', function(event) {
        event.preventDefault();

        $.post($SCRIPT_ROOT + '/empty', {
            time : 'asd',

        }).done(function(response) {
            console.log('Pip') //test
            let tbl = document.querySelector("#confirmevents")
            //tbl = $("#confirmevents");
            console.log('Chdildren: ', tbl.childNodes())
            /*
            for (child in tbl.children() )  {
                child.hide()
            };
            */
            //child = tbl.firstChild;
            //console.log("firs: ",tbl.firstChild);
            //console.log("seocn d: ",child.firstChild);
            //while (child.firstChild) {
            //tbl.removeChild(child.firstChild);
            var new_tbody = document.createElement('tbody');
            //populate_with_new_rows(new_tbody);
            //tbl.parentNode.replaceChild(new_tbody, old_tbody)
            
        }).fail(function() {
            // Debug
            console.log("Failed to empty")
        });
    });
  });

