$(function()  {  

        let table = document.querySelector("#confirmevents");

        function generateTableHead(table) {
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
        generateTableHead(table);

        $('#eventsubmits').bind('click', function(event) {

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
        */
        
        // Add a row to the confirmation table
        function appendRow(table) {
            
            let items = [globals.ev, globals.dr]
            console.log("items: ", items)
            let row_append = table.insertRow(-1);
            for (let item of items) {
            let text = document.createTextNode(item);
            let cell = row_append.insertCell();
            cell.appendChild(text)
        
            }
        }
        
        // If table exists, append new row.
        console.log(table)
        console.log("rows.length", table.rows.length)
        console.log("table; response_obj status: ", globals.response_obj);

        if ((table.rows.length > 0) && 
                (globals.response_obj !== undefined)) {
            appendRow(table);
        } 
        console.log("globals after table: ", globals)

    });
});

