// Functions for asynch requets to delete or 
// remove a event from buffer

$(function() {
    $('#EditBufferButton').on('click', function(event) {
        event.preventDefault();

        // Finds the closest row <tr>
        var $row = $(this).closest("tr"),        
        var button = document.getElementById('EditBufferButton');

            /* TESTING
        // Finds all children <td> elements
        $tds = $row.find("td");             
        console.log("td's", $tds)

        // Visits every single <td> element
        $.each($tds, function() {               
        // Prints out the text within the <td>
        console.log($(this).text());        
        });
        */
        $.post($SCRIPT_ROOT + '/editRow', {
            value: 'edit',
            id : button.dataset.idx 
        }).done(function(response) {
            // Reload the table the row from table
            // TESTING
            console.log('editbutton post OK')
        }).fail(function() {
            // TESTING
            console.log('editbutton post FAIL')
        });
    });
  });


$(function() {
    $('#DeleteBufferButton').on('click', function(event) {
        event.preventDefault();

        // Finds the closest row <tr>
        var $row = $(this).closest("tr");       
        var button = document.getElementById('DeleteBufferButton');

        $.post($SCRIPT_ROOT + '/delete_row_buffer', {
            value: 'delete',
            id : button.dataset.idx 
        }).done(function(response) {
            // Delete the tr
            $row.remove();
        }).fail(function(error) {
            console.log('Failed to remove single entry')
        });
    });
  });
