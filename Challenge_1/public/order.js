/*
  order.js file for the menu items display and ordering an item from the menu
*/
document.addEventListener('DOMContentLoaded', () => {

  // Define most used elements such as the menu and order grid containers, templates, and order form

  let menu = document.querySelector('.menu-container');
  let template = document.querySelector('template');
  let order_form = document.querySelector('form');
  let select = document.querySelector('select');
  let menu_items;
  let cost_element = document.querySelector("#cost");
  let cost = Number(cost_element.innerText.slice(7));
  let quantity = document.querySelector('#quantity');
  // fetch the menu to populate the html page
  fetch('/menu')
    .then(response => response.json())
    .then(data => {
      menu_items = data['menu_items'];
      // iterate through each item in the response object
      for (var i = 0; i < menu_items.length; i++) {
        // use templating to display the menu items 
        menu.insertAdjacentHTML('beforeend', template.innerHTML);
        let row = menu.lastElementChild;
        row.setAttribute('id', menu_items[i]['item_id']);
        let columns = row.querySelectorAll('span');
        columns[0].innerText = menu_items[i]['name'];
        columns[1].innerText = '$' + menu_items[i]['price'];
        let select = order_form.querySelector('select');
        let option = document.createElement('option');
        option.setAttribute('value', columns[0].innerText);
        option.innerText = option.getAttribute('value');
        select.appendChild(option);
      }
      /*
          function server_request is used to make fetch requests to the server
          @params takes in the url of the route, the data that goes with it, the action verb, and callback 
          function to return to a specific function
  
      */
      function server_request(url, data = {}, verb, callback) {
        return fetch(url, {
          credentials: 'same-origin',
          method: verb,
          body: JSON.stringify(data),
          headers: { 'Content-Type': 'application/json' }
        })
          .then(response => response.json())
          .then(response => {
            if (callback)
              // invoke the callback function passing in response we got from query
              callback(response);
          })
          .catch(error => console.error('Error:', error));
      }
      // event listener for the order form select item
      select.addEventListener('change', (e) => {
        let option = select.value;
        for (var i = 0; i < menu_items.length; i++) {
          if (menu_items[i]['name'] === option) {
            // event listener for the quantity
            quantity.addEventListener('change', (e) => {
              e.preventDefault();
              // update the cost dynamically with quantity
              cost = menu_items[i]['price'] * Number(quantity.value);
              cost_element.innerHTML = 'Cost: $' + cost.toFixed(2);
            });
            break;
          }
        }
      });

      // order form event listener
      order_form.addEventListener('submit', (event) => {
        event.preventDefault();
        // get needed attribute values for function call to the server
        const action = order_form.getAttribute('action');
        const method = order_form.getAttribute('method');
        const data = Object.fromEntries(new FormData(order_form).entries());
        // make sure to include the default status value
        data['status'] = 'Pending';
        // update our data object with the correct attribute values
        for (var i = 0; i < menu_items.length; i++) {
          if (menu_items[i]['name'] === data['item_id']) {
            data['item_name'] = i;
            data['item_id'] = menu_items[i]['item_id'];
            break;
          }
        }
        // make a server request to the database to add the order to the orders db
        server_request(action, data, method, (response) => {
          // reset form fields
          //order_form.reset();
          cost_element.innerHTML = 'Cost: $0';

        })
      })
    })
    .catch(err => {
      console.error(err);
    });
});