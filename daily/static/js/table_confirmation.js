/* Generate table on button click,
 * If table exists just append row(s) into the table
 */
$(function()  {  

        let table = document.querySelector("#confirmevents");
        globals.table_confirm = table
        console.log("Globals table :", globals)

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

        globals.addRow = function addRow(table) {

            console.log("Addrow ran")
            // Append row to table
            function appendRow(table) {
                
                let items = [globals.ev, globals.dr]
                console.log("items: ", items)
                let row_append = table.insertRow(-1);
                for (let item of items) {
                    let text = document.createTextNode(item);
                    let cell = row_append.insertCell();
                    cell.appendChild(text);
                }
            }
            
            // If table exists, append new row.

            // TEST
            console.log("table; response_obj status: ", 
                globals.response_obj);

            if ((table.rows.length > 0) && 
                    (globals.response_obj !== undefined)) {
                appendRow(table);
            } 
            console.log("globals after table: ", globals)
        }
});

