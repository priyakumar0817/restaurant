/*
    admin.js page responsible for CRUD operations on the menu items, and displaying current orders
*/
document.addEventListener('DOMContentLoaded', () => {

    // Define most used elements such as the menu and order grid containers, templates, and CRUD forms
    let menu = document.querySelector('.menu-container');
    let order_table = document.querySelector('.grid-container');
    let template = document.querySelector('menutemplate');
    let order_template = document.querySelector('ordertemplate');
    let delete_form = document.getElementById('delete-order');
    let add_form = document.getElementById('add-order');
    let update_form = document.getElementById('update-order');
    let orders, menu_items;
    let order;
    /*
        function server_request is used to make fetch requests to the server
        @params takes in the url of the route, the data that goes with it, the action verb, and callback 
        function to return to a specific function

    */
    function server_request(url, data, verb, callback) {
        // server fetch request
        return fetch(url, {
            credentials: 'same-origin',
            method: verb,
            body: JSON.stringify(data),
            headers: { 'Content-Type': 'application/json' }
        })
            .then(response => response.json())
            .then(response => {
                if (callback)
                    callback(response);
            })
            // catch any errors if fetch failed
            .catch(error => console.error('Error:', error));
    }
    // fetch the menu items from the menu_items database
    fetch('/menu')
        .then(response => response.json())
        .then(data => {

            menu_items = data['menu_items'];
            // invoke populate_penu passing in the items retrieved
            populate_menu(menu_items);

        }).catch(err => {
            console.error(err);
        });

    /*
        populated the html page with the given menu items and attaches event listeners for each
        menu crud operation
    */
    function populate_menu(menu_items) {
        // iterate through all the menu items and update their corresponding elements
        for (var i = 0; i < menu_items.length; i++) {
            // insert into the container using templating
            menu.insertAdjacentHTML('beforeend', template.innerHTML);
            let row = menu.lastElementChild;
            row.setAttribute('id', menu_items[i]['item_id']);
            let columns = row.querySelectorAll('span');
            // include the id with the menu item this time
            columns[0].innerText = menu_items[i]['name'] + ": " + menu_items[i]['item_id'];
            columns[1].innerText = '$' + menu_items[i]['price'];
        }

        // event listener for the add menu item form
        add_form.addEventListener('submit', (event) => {
            event.preventDefault();
            // get the needed data values for the server request
            const method = add_form.getAttribute('method');
            let data = Object.fromEntries(new FormData(add_form).entries());
            const action = add_form.getAttribute('action');
            let new_item = data;
            // make a server request to POST 
            server_request(action, data, method, (response) => {
                // add the new item to the menu display using templating
                menu.insertAdjacentHTML('beforeend', template.innerHTML);
                let row = menu.lastElementChild;
                // set the id to the returned new id
                row.setAttribute('id', response);
                let columns = row.querySelectorAll('span');
                columns[0].innerText = new_item['name'] + ": " + response;
                columns[1].innerText = '$' + new_item['price'];
            })
            // reset the form after completing query
            add_form.reset();
        })


        // update form event listener for updating current menu item
        update_form.addEventListener('submit', (event) => {
            event.preventDefault();
            // retrieve necessary data values for server request call
            const method = update_form.getAttribute('method');
            let data = Object.fromEntries(new FormData(update_form).entries());
            const action = update_form.getAttribute('action') + '/' + data['id'];
            // make the PUT request
            server_request(action, data, method, (response) => {
                // validate response, only update if response was successful
                if (response.success) {
                    let did = data['id'];
                    // update all the corresponding items on the orders page
                    document.querySelectorAll(`[id="${did}"]`).forEach(item => {
                        console.log(item.children[0])
                        // update for both the menu container and the orders container
                        if (item.parentNode.getAttribute('class') == 'menu-container') {
                            item.children[0].innerText = data['name'] + ": " + did;
                            console.log(item.children[0].innerText);
                        } else {
                            item.children[2].innerText = data['name'];
                            console.log(item.children[2].innerText);
                        }
                    })
                } else {
                    // if failed then display alert
                    alert("Error updating entry.")
                }
                // reset the form after completion of menu update
                update_form.reset();
            })

        })

        // event listener for delete menu item form button 
        delete_form.addEventListener('submit', (event) => {
            event.preventDefault();
            // get necessary form attributes
            const method = delete_form.getAttribute('method');
            let data = Object.fromEntries(new FormData(delete_form).entries());
            // get the id value from the data object
            data = data['id'];
            const action = delete_form.getAttribute('action') + '/' + data;
            // make a server DELETE request passing in the primary key id
            server_request(`/orders/${data}`, data, method, (response) => {
                // make another server request for the menu item
                server_request(action, data, method, (response) => {
                    // only update page if the deletion was successful
                    if (response.success) {
                        console.log(`[id="${data}"]`);
                        document.querySelectorAll(`[id="${data}"]`).forEach(item => item.remove());
                        console.log(response);
                    } else {
                        alert("Error deleting entry.")
                    }
                })
                // reset the form when finished clicking button
                delete_form.reset();
            })

        })
    }
    /*
        function to retrieve the current orders from the database
    */
    function getOrder(ord) {
        order = ord;
        return order;
    }
    // fetch current orders from the database
    fetch('/orders')
        .then(response => response.json())
        .then(data => {
            orders = data['orders'];
            getOrder(orders);
            // update the html page with the orders using templating
            for (var i = 0; i < orders.length; i++) {
                order_table.insertAdjacentHTML('beforeend', order_template.innerHTML);
                let row = order_table.lastElementChild;
                row.setAttribute('id', orders[i]['item_id']);
                let columns = row.querySelectorAll('span');
                columns[0].innerText = orders[i]['name'];
                // fetch the menu items as well
                fetch(`/menu/${orders[i]["item_id"]}`)
                    .then(response => response.json())
                    .then(item_info => {
                        // get the name and id of the menu item
                        columns[1].innerText = item_info['name'];
                        columns[2].innerText = item_info['item_id'];
                    }).catch(err => console.error('Error:', err));
                let status = row.lastElementChild;
                let order_item = orders[i];
                // update status button if needed from database
                if (order_item['status'] == 'Complete') {
                    status.style.backgroundColor = 'lightgreen';
                }
                status.setAttribute('value', order_item['status']);
                // event listener for status button
                status.addEventListener('click', (e) => {
                    // update the status button
                    if (order_item['status'] === 'Complete') {
                        order_item['status'] = 'Pending';
                    } else {
                        order_item['status'] = 'Complete';
                    }
                    e.preventDefault();
                    let url = `/orders/${order_item['order_id']}`;
                    // update the status in the database too
                    server_request(url, order_item, 'PUT', function (response) {
                        console.log(response);
                        if (response.success) {
                            status.setAttribute('value', order_item['status']);
                            if (order_item['status'] == 'Complete') {
                                status.style.backgroundColor = 'lightgreen';
                            } else {
                                status.style.backgroundColor = 'yellow';
                            }
                        }
                    });
                });
            }
        })
        .catch(err => {
            console.error(err);
        });

});