
// Edit buffer rows
$(function() {
    $('.buffer_button.edit').on('click', function(event) {
        event.preventDefault();

        /*
        // Finds the delete button
        var button= this.closest(".edit");       
        var row = this.closest("tr")

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
        */
    });
  });


// Delete buffer rows
$(function() {
    $('.buffer_button.delete').on('click', function(event) {
        event.preventDefault();

        // Finds the delete button
        var button= this.closest(".delete");       
        var row = this.closest("tr")

        $.post($SCRIPT_ROOT + '/delete_row_buffer', {
            value: 'delete',
            id:     button.dataset.idx,
        }).done(function(response) {
            // Delete the tr
            row.remove();
        }).fail(function(error) {
        });
    });
  });

// Delete all buffer rows
$(function() {
    $('#eventclear').on('click', function(event) {
        event.preventDefault();

        $.post($SCRIPT_ROOT + '/empty', {

        }).done(function(response) {
            //Jqueyr altenative
            //tbl = $("#confirmevents");
            
            // find table 'confirmevents'
            let tbl = document.getElementsByTagName('table')[0];
            tbl.remove();
        }).fail(function() {
            console.log("Failed to empty")
        });
    });
  });

