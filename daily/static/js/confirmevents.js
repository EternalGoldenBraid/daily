  $(function() {
    $('#eventsubmits').bind('click', function(event) {
        event.preventDefault();
	let ev = $('input[name="event"]').val();
	let dr = $('input[name="duration_event"]').val();
        let description={"event": ev, "duration": dr};

        $.post($SCRIPT_ROOT + '/events_confirm', {
	    event: ev,
	    duration: dr 
        }).done(function(response) {

        // Testing
        if (globals.response_obj) {
            global.response_obj = response;
        }
        $('#result').text(response);
        console.log(`response before loop: ${Object.keys(response)}, event: ${ev}`)
        for (let [key, value] of Object.entries(response)) {
        console.log("response: ", `${key}: ${value}`)
        };

        if (ev in Object.keys(response)) {
            throw "Entry already exists"
        }
            /*
	// Generate table based on response
        function generateTableHead(table, keys) {
            let thead = table.createTHead();
            let row = thead.insertRow();
            var labels = ['Event', 'Duration'];
					
            for (let label of labels) {
                let th = document.createElement("th");
		let text = document.createTextNode(label);
		th.appendChild(text);
		row.appendChild(th);
          }
        }
         function generateTable(table, data) {

             for(let entry of Object.entries(data)) {
                 let row = table.insertRow();

                 for(let item of entry) {
                     let cell =row.insertCell();
                     let text = document.createTextNode(item);
                     cell.appendChild(text);
                 }
            }
	}

        // Add a row to the confirmation table
        function appendRow(table) {
            
            let items = [ev, dr]
            console.log("items: ", items)
            let row_append = table.insertRow(-1);
            for (let item of items) {
            let text = document.createTextNode(item);
            let cell = row_append.insertCell();
            cell.appendChild(text)

            }
        }

        let table = document.querySelector("#confirmevents");

        // If table exists, append new row. Else create table for confirms
        console.log(table)
        table.rows.length
        if (table.rows.length === 0) {
            let keys= Object.keys(response);
            generateTableHead(table, keys);
            generateTable(table, response);
        } 
        else {
            appendRow(table);
        }
        */

        }).fail(function() {
            // Debug
            console.error();
        });
    });
  });
