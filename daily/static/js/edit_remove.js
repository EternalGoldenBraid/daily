
$(function() {
    $('#deleteRowButton').on('click', function(event) {
        event.preventDefault();

    // Finds the closest row <tr>
    var $row = $(this).closest("tr"),        

    // Finds all children <td> elements
    $tds = $row.find("td");             
    console.log("td's", $tds)

    // Visits every single <td> element
    $.each($tds, function() {               

    // Prints out the text within the <td>
    console.log($(this).text());        
    });
        $.post($SCRIPT_ROOT + '/deleteRow', {

        }).done(function(response) {
            // Delete the tr
        }).fail(function() {

        });
    });
  });


$(function() {
    $('#editRowButton').on('click', function(event) {
        event.preventDefault();

        // Finds the closest row <tr>
        var $row = $(this).closest("tr"),        

        // Finds all children <td> elements
        $tds = $row.find("td");             
        console.log("td's", $tds)

        // Visits every single <td> element
        $.each($tds, function() {               
        // Prints out the text within the <td>
        console.log($(this).text());        
        });
        $.post($SCRIPT_ROOT + '/editRow', {

        }).done(function(response) {
            // Reload the table the row from table
        }).fail(function() {

        });
    });
  });
