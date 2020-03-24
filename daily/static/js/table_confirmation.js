$(function()  {  
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

    if (table.rows.length === 0 $$ globals.response_obj !=== undefined){
        let keys= Object.keys(globals.response_obj);
        generateTableHead(table, keys);
        generateTable(table, globals.response_obj);
    } 
    else {
        appendRow(table);
    }
    
    
})

